import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

from utils.plotting import barplot, pieplot, donutplot, boxplot_by_category, heatmap

from utils.queries import (
    get_most_visited_hospitals,
    get_most_visited_departments,
    get_department_patient_doctor_ratio,
    get_patient_age_gender_distribution,
    get_monthly_appointment_trend,
    get_appointment_status_ratio,
    get_patient_age_groups,
    get_hospital_avg_rating,
    get_patient_age_by_hospital_for_boxplot,
    get_total_patients,
    get_total_appointments,
    get_total_doctors
)

from utils.database import run_query

# 页面配置
st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("Hospital Analytics Dashboard")
st.markdown("---")

# ==================== Hospital Analytics ====================
with st.expander("Hospital and Departmental Analytics", expanded=True):
    
    # Most Frequently Visited Hospitals
    st.subheader("Most Frequently Visited Hospitals")
    df_hospitals = get_most_visited_hospitals()
    
    if df_hospitals is not None and not df_hospitals.empty:
        # 准备数据字典
        hospital_freq = dict(zip(df_hospitals['hospital_name'], df_hospitals['visit_count']))
        
        # 使用你的自定义 barplot
        fig, ax = barplot(
            data=hospital_freq,
            title='Most Frequently Visited Hospitals',
            xlabel='Hospital Name',
            ylabel='Visit Count',
            horizontal=True,
            show_values=True,
            color=True,
            sort_values=True,
            figsize=(12, 8)
        )
        
        st.pyplot(fig)
        
        # 显示数据表
        if st.checkbox("View Most Frequently Visited Hospitals Table"):
            st.dataframe(df_hospitals, use_container_width=True)
    else:
        st.warning("No hospital data available")
    
    st.markdown("---")

    # Most Frequently Visited Departments
    st.subheader("Most Frequently Visited Departments")
    df_departments = get_most_visited_departments()
    
    if df_departments is not None and not df_departments.empty:
        # 准备数据字典
        # 合并医院和科室名称
        df_departments['full_name'] = df_departments['hospital_name'] + ' - ' + df_departments['department_name']
        
        department_freq = dict(zip(df_departments['full_name'], df_departments['frequency']))
        
        # 使用你的自定义 barplot
        fig, ax = barplot(
            data=department_freq,
            title='Most Frequently Visited Departments',
            xlabel='Department Name',
            ylabel='Visit Count',
            horizontal=True,
            show_values=True,
            color=True,
            sort_values=True,
            figsize=(12, 8)
        )
        
        st.pyplot(fig)
        
        # 显示数据表
        if st.checkbox("View Most Frequently Visited Departments Table"):
            st.dataframe(df_departments, use_container_width=True)
    else:
        st.warning("No department data available")
    
    st.markdown("---")
    
    # Department Patient-Doctor Ratio
    st.subheader("Departments with Highest Patient-Doctor Ratios")
    df_ratio = get_department_patient_doctor_ratio()
    
    if df_ratio is not None and not df_ratio.empty:
        # 合并医院和科室名称
        df_ratio['full_name'] = df_ratio['hospital_name'] + ' - ' + df_ratio['department_name']
        
        fig, ax = barplot(
            data=None,
            x=df_ratio['full_name'].values,
            y=df_ratio['patient_doctor_ratio'].values,
            title='Departments with Highest Patient-Doctor Ratio',
            xlabel='Department',
            ylabel='Patient-Doctor Ratio',
            horizontal=True,
            show_values=True,
            sort_values=True,
            value_format='.1f',
            figsize=(12, 8)
        )
        
        st.pyplot(fig)
        
        if st.checkbox("View Detailed Statistics"):
            st.dataframe(df_ratio[['department_name', 'doctor_count', 'patient_count', 'patient_doctor_ratio']], 
                        use_container_width=True)
    else:
        st.warning("No department ratio data available")
    
    st.markdown("---")
    
    # Hospital Average Rating
    st.subheader("Hospital Average Ratings")
    df_rating = get_hospital_avg_rating()
    
    if df_rating is not None and not df_rating.empty:
        fig, ax = barplot(
            data=None,
            x=df_rating['hospital_name'].values,
            y=df_rating['avg_rating'].values,
            title='Hospital Average Ratings Based on Doctor Ratings',
            xlabel='Hospital Name',
            ylabel='Average Rating',
            horizontal=True,
            show_values=True,
            value_format='.2f',
            sort_values=True,
            ascending=False,
            figsize=(12, 8)
        )
        
        st.pyplot(fig)
    else:
        st.warning("No rating data available")

# ==================== Appointment Analytics ====================
with st.expander("Appointment Analytics", expanded=False):
    
    # Monthly Appointment Trend
    st.subheader("Monthly Appointment Trends")
    df_monthly = get_monthly_appointment_trend()
    
    if df_monthly is not None and not df_monthly.empty:
        fig, ax = barplot(
            data=None,
            x=df_monthly['month'].values,
            y=df_monthly['appointment_num'].values,
            title='Monthly Appointment Trends',
            xlabel='Month',
            ylabel='Number of Appointments',
            show_values=True,
            sort_values=False,
            figsize=(12, 6)
        )
        
        st.pyplot(fig)
    else:
        st.warning("No monthly trend data available")
    
    st.markdown("---")
    
    # Appointment Status Overview
    st.subheader("Appointment Status Overview")
    df_status = get_appointment_status_ratio()
    
    if df_status is not None and not df_status.empty:
        # 转换为字典
        status_dict = df_status.iloc[0].to_dict()
        
        total_appointments = get_total_appointments()
        status_counts = {
            'Scheduled': status_dict['scheduled'] * total_appointments,
            'Cancelled': status_dict['cancelled'] * total_appointments,
            'Completed': status_dict['completed'] * total_appointments
        }
        
        fig, ax = donutplot(
            data=status_counts,
            title='Appointment Status Overview',
            palette='pastel',
            center_text=f'Total\n{int(total_appointments)}',
            legend=True,
            figsize=(10, 8)
        )
        
        st.pyplot(fig)
    else:
        st.warning("No appointment status data available")

# ==================== Patient Demographics ====================
with st.expander("Patient Demographics", expanded=False):
    
    # Patient Age Distribution
    st.subheader("Patient Age Distribution")
    df_age = get_patient_age_groups()
    
    if df_age is not None and not df_age.empty:
        # 转换为 Series
        age_series = pd.Series(df_age['count'].values, index=df_age['age_group'].values)
        
        fig, ax = pieplot(
            data=age_series,
            title="Patient Age Distribution",
            palette="rocket",
            textcolor='white',
            figsize=(10, 8)
        )
        
        st.pyplot(fig)
    else:
        st.warning("No age distribution data available")
    
    st.markdown("---")
    
    # Gender Distribution
    st.subheader("Patient Gender Distribution")
    df_gender = get_patient_age_gender_distribution()
    
    if df_gender is not None and not df_gender.empty:
        gender_counts = df_gender.groupby('gender')['count'].sum().reset_index()
        
        fig, ax = pieplot(
            data=None,
            x=gender_counts['gender'].values,
            y=gender_counts['count'].values,
            title="Patient Gender Distribution",
            palette='Set2',
            figsize=(8, 8)
        )
        
        st.pyplot(fig)
    else:
        st.warning("No gender distribution data available")
    
    st.markdown("---")
    
    # Patient Age by Hospital (Box Plot)
    st.subheader("Patient Age Distribution by Hospital")
    df_age_hospital = get_patient_age_by_hospital_for_boxplot()
    
    if df_age_hospital is not None and not df_age_hospital.empty:
        fig, ax = boxplot_by_category(
            data=df_age_hospital,
            x_col='hospital_name',
            y_col='age',
            title='Patient Age Distribution by Hospital',
            xlabel='Hospital Name',
            ylabel='Age (years)',
            palette='Set2',
            show_mean=True,
            rotation=45,
            figsize=(14, 8)
        )
        
        st.pyplot(fig)
        
        # 显示统计信息
        if st.checkbox("View Statistical Summary"):
            stats = df_age_hospital.groupby('hospital_name')['age'].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('median', 'median'),
                ('std', 'std'),
                ('min', 'min'),
                ('max', 'max')
            ]).round(2)
            st.dataframe(stats, use_container_width=True)
    else:
        st.warning("No age by hospital data available")


# 侧边栏
with st.sidebar:
    st.title("Analytics Controls")
    st.markdown("---")
    
    st.subheader("About")
    st.write("This dashboard uses customized matplotlib/seaborn plotting functions to provide:")
    st.write("• Hospital utilization metrics")
    st.write("• Appointment analytics")
    st.write("• Patient demographics")
    st.write("• Individual patient tracking")
    
    st.markdown("---")
    
    # 导入必要的函数
    from utils.queries import get_total_appointments
    
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()
    
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("app.py")