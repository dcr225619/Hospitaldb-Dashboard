import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

from utils.queries import (
    search_patients,
    get_patient_blood_chemistry,
    get_patient_vitamin_levels
)

from utils.database import run_query

# ==================== Individual Patient Tracking ====================

with st.expander("Individual Patient Tracking", expanded=True):
    
    st.subheader("Search for a Patient")
    
    search_term = st.text_input(
        "Enter patient name or email:", 
        placeholder="e.g., John Smith or john@email.com"
    )
    
    if search_term:
        df_patients = search_patients(search_term)
        
        if df_patients is not None and not df_patients.empty:
            st.write(f"Found {len(df_patients)} patient(s):")
            
            selected_patient = st.selectbox(
                "Select a patient:",
                options=df_patients['patient_id'].tolist(),
                format_func=lambda x: df_patients[df_patients['patient_id'] == x]['full_name'].values[0]
            )

            if selected_patient:
                selected_patient = int(selected_patient)
                
                patient_info = df_patients[df_patients['patient_id'] == selected_patient].iloc[0]
                
                # 显示患者基本信息
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Name", patient_info['full_name'])
                with col2:
                    st.metric("ID", selected_patient)
                with col3:
                    st.metric("Gender", patient_info['gender'])
                with col4:
                    st.metric("Date of Birth", patient_info['date_of_birth'])
                
                st.markdown("---")
                
                # Blood Chemistry Panel
                st.subheader("Blood Chemistry Panel Over Time")
                df_blood = get_patient_blood_chemistry(selected_patient)

                if df_blood is not None and not df_blood.empty:
                    # 检查是否有任何非空的血液化学数据
                    has_data = df_blood[['total_cholesterol', 'ldl', 'hdl', 'triglycerides', 
                                        'hemoglobin', 'wbc', 'rbc', 'platelets']].notna().any().any()
                    
                    if has_data:
                        metrics = st.multiselect(
                            "Select metrics to display:",
                            ['total_cholesterol', 'ldl', 'hdl', 'triglycerides', 
                            'hemoglobin', 'wbc', 'rbc', 'platelets'],
                            default=['total_cholesterol', 'ldl', 'hdl']
                        )
                        
                        if metrics:
                            fig = go.Figure()
                            
                            for metric in metrics:
                                # 只绘制有数据的指标
                                if metric in df_blood.columns and df_blood[metric].notna().any():
                                    fig.add_trace(go.Scatter(
                                        x=df_blood['date_of_visit'],
                                        y=df_blood[metric],
                                        mode='lines+markers',
                                        name=metric.replace('_', ' ').title()
                                    ))
                            
                            if fig.data:  # 如果有数据被添加
                                fig.update_layout(
                                    title='Blood Chemistry Trends',
                                    xaxis_title='Date',
                                    yaxis_title='Value',
                                    height=500,
                                    hovermode='x unified'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Selected metrics have no data for this patient")
                        else:
                            st.info("Please select at least one metric")
                    else:
                        st.warning("No blood chemistry data available for this patient")
                else:
                    st.warning("No records found for this patient")
                
                st.markdown("---")
                
                # Vitamin D Levels
                st.subheader("Vitamin D Levels Over Time")
                df_vitamins = get_patient_vitamin_levels(selected_patient)

                if df_vitamins is not None and not df_vitamins.empty:
                    # 检查是否有任何维生素D数据
                    has_vitamin_data = df_vitamins[['vitamin_d2', 'vitamin_d3', 'vitamin_d_total']].notna().any().any()
                    
                    if has_vitamin_data:
                        fig = go.Figure()
                        
                        for col in ['vitamin_d2', 'vitamin_d3', 'vitamin_d_total']:
                            if col in df_vitamins.columns and df_vitamins[col].notna().any():
                                fig.add_trace(go.Scatter(
                                    x=df_vitamins['date_of_visit'],
                                    y=df_vitamins[col],
                                    mode='lines+markers',
                                    name=col.replace('_', ' ').title()
                                ))
                        
                        fig.update_layout(
                            title='Vitamin D Levels Trend',
                            xaxis_title='Date',
                            yaxis_title='Level (ng/mL)',
                            height=500,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No vitamin D data available for this patient")
                else:
                    st.warning("No vitamin D records found for this patient")
        else:
            st.info("No patients found matching your search")
    else:
        st.info("Enter a search term to find patients")