# pages/predictions.py

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.predictions import hospital_revenue_prediction

st.set_page_config(page_title="ARIMA Predictions", layout="wide")

st.title("Hospital Revenue Predictions - ARIMA vs Linear Regression")



arima_predictions_dict, predictions_dict = hospital_revenue_prediction()

# ==================== 侧边栏控制 ====================
with st.sidebar:
    st.header("Display Options")
    
    # 选择要显示的医院
    all_hospitals = list(arima_predictions_dict.keys())
    selected_hospitals = st.multiselect(
        "Select Hospitals to Display:",
        options=all_hospitals,
        default=all_hospitals[:6]  # 默认显示前6个
    )
    
    st.markdown("---")
    
    # 是否显示线性回归
    show_lr = st.checkbox("Show Linear Regression", value=True)
    
    # 是否显示置信区间
    show_ci = st.checkbox("Show Confidence Interval", value=True)
    
    st.markdown("---")
    
    # 图表高度调整
    chart_height = st.slider("Chart Height per Row (px):", 300, 600, 400, 50)

# ==================== 主要统计信息 ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_aic = np.mean([d['aic'] for d in arima_predictions_dict.values()])
    st.metric("Average AIC", f"{avg_aic:.1f}")

with col2:
    st.metric("Total Hospitals", len(arima_predictions_dict))

with col3:
    avg_forecast = np.mean([d['forecast'][0] for d in arima_predictions_dict.values()])
    st.metric("Avg Next Month Forecast", f"${avg_forecast:,.0f}")

with col4:
    growth_rate = np.mean([
        (d['forecast'][2] / d['historical_data']['amount'].iloc[-1] - 1) * 100
        for d in arima_predictions_dict.values()
    ])
    st.metric("Avg 3-Month Growth", f"{growth_rate:.1f}%")

st.markdown("---")

# ==================== 绘制图表 ====================
if not selected_hospitals:
    st.warning("Please select at least one hospital to display")
else:
    # 过滤数据
    filtered_arima = {k: v for k, v in arima_predictions_dict.items() if k in selected_hospitals}
    filtered_lr = {k: v for k, v in predictions_dict.items() if k in selected_hospitals} if show_lr else {}
    
    # 计算子图布局
    n_hospitals = len(filtered_arima)
    n_cols = 3
    n_rows = (n_hospitals + n_cols - 1) // n_cols
    
    # 创建子图
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=[f'<b>Hospital {hid}</b>' for hid in filtered_arima.keys()],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
        specs=[[{"secondary_y": False} for _ in range(n_cols)] for _ in range(n_rows)]
    )
    
    # 遍历每个医院
    for idx, (hospital_id, arima_data) in enumerate(filtered_arima.items()):
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        
        # 历史数据
        hist_data = arima_data['historical_data'].sort_values('year_month')
        x_hist = list(range(len(hist_data)))
        y_hist = hist_data['amount'].values
        
        # 添加历史数据线
        fig.add_trace(
            go.Scatter(
                x=x_hist,
                y=y_hist,
                mode='lines+markers',
                name='Historical',
                line=dict(color='#1f77b4', width=2.5),
                marker=dict(size=5),
                legendgroup=f'g{idx}',
                showlegend=(idx == 0),
                hovertemplate='<b>Month %{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
            ),
            row=row, col=col
        )
        
        # 预测数据
        future_x = [len(hist_data) - 1, len(hist_data), len(hist_data) + 1, len(hist_data) + 2]
        future_y = [y_hist[-1]] + list(arima_data['forecast'])
        
        # ARIMA预测
        fig.add_trace(
            go.Scatter(
                x=future_x,
                y=future_y,
                mode='lines+markers',
                name='ARIMA',
                line=dict(color='#ff7f0e', width=2.5, dash='dash'),
                marker=dict(size=8, symbol='square'),
                legendgroup=f'g{idx}',
                showlegend=(idx == 0),
                hovertemplate='<b>Forecast Month %{x}</b><br>Predicted: $%{y:,.0f}<extra></extra>'
            ),
            row=row, col=col
        )
        
        # 置信区间
        if show_ci:
            ci = arima_data['conf_int']
            fig.add_trace(
                go.Scatter(
                    x=future_x[1:] + future_x[1:][::-1],
                    y=list(ci[:, 1]) + list(ci[:, 0])[::-1],
                    fill='toself',
                    fillcolor='rgba(255, 127, 14, 0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=(idx == 0),
                    name='95% CI',
                    legendgroup=f'g{idx}',
                    hoverinfo='skip'
                ),
                row=row, col=col
            )
        
        # 线性回归
        if show_lr and hospital_id in filtered_lr:
            lr_forecast = filtered_lr[hospital_id]['future_predictions']
            lr_future_y = [y_hist[-1]] + list(lr_forecast)
            
            fig.add_trace(
                go.Scatter(
                    x=future_x,
                    y=lr_future_y,
                    mode='lines+markers',
                    name='Linear Reg.',
                    line=dict(color='#2ca02c', width=2.5, dash='dot'),
                    marker=dict(size=8, symbol='triangle-up'),
                    legendgroup=f'g{idx}',
                    showlegend=(idx == 0),
                    hovertemplate='<b>LR Forecast %{x}</b><br>Predicted: $%{y:,.0f}<extra></extra>'
                ),
                row=row, col=col
            )
        
        # 更新子图标题
        optimal_order = arima_data['optimal_order']
        aic = arima_data['aic']
        fig.layout.annotations[idx].update(
            text=f'<b>Hospital {hospital_id}</b><br><i>ARIMA{optimal_order} | AIC={aic:.1f}</i>',
            font=dict(size=11)
        )
        
        # 更新轴
        fig.update_xaxes(
            title_text='Month Index' if row == n_rows else '',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            row=row, col=col
        )
        fig.update_yaxes(
            title_text='Revenue ($)' if col == 1 else '',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            row=row, col=col
        )
    
    # 更新整体布局
    fig.update_layout(
        height=chart_height * n_rows,
        showlegend=True,
        legend=dict(        # 图例位于右上方
            orientation="v", 
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,     
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11)
        ),
        hovermode='closest',
        template='plotly_white',
        title=dict(
            text='<b>ARIMA Revenue Predictions Comparison</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        )
    )
    
    # 在 Streamlit 中显示
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 数据表格 ====================
    with st.expander("View Detailed Predictions"):
        for hospital_id in selected_hospitals:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**Hospital {hospital_id}**")
                st.write(f"ARIMA Order: {arima_predictions_dict[hospital_id]['optimal_order']}")
                st.write(f"AIC: {arima_predictions_dict[hospital_id]['aic']:.2f}")
            
            with col2:
                pred_df = pd.DataFrame({
                    'Month': ['Next', '+2 Months', '+3 Months'],
                    'ARIMA': arima_predictions_dict[hospital_id]['forecast'],
                    'Lower CI': arima_predictions_dict[hospital_id]['conf_int'][:, 0],
                    'Upper CI': arima_predictions_dict[hospital_id]['conf_int'][:, 1],
                })
                
                if show_lr and hospital_id in predictions_dict:
                    pred_df['Linear Reg.'] = predictions_dict[hospital_id]['future_predictions']
                
                st.dataframe(
                    pred_df.style.format({
                        'ARIMA': '${:,.0f}',
                        'Lower CI': '${:,.0f}',
                        'Upper CI': '${:,.0f}',
                        'Linear Reg.': '${:,.0f}'
                    }),
                    use_container_width=True
                )
            
            st.markdown("---")