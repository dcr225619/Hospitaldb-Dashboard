# app.py
import streamlit as st
from config import PAGE_CONFIG
from utils.database import test_connection
from utils.queries import (
    get_total_patients, 
    get_total_appointments, 
    get_total_doctors,
    get_today_appointments
)
import os

# 页面配置
st.set_page_config(**PAGE_CONFIG)

# 自定义 CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-header"> Hospital Management System</div>', unsafe_allow_html=True)
st.markdown("---")

# 测试数据库连接
if not test_connection():
    st.error("Database connection failed! Please check your configuration in config.py")
    st.stop()
else:
    st.success("Database connected successfully!")

# 关键指标卡片
st.subheader("Key Metrics Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_patients = get_total_patients()
    st.metric(
        label="👥 Total Patients",
        value=f"{total_patients:,}",
        delta="Active"
    )

with col2:
    today_appointments = get_today_appointments()
    st.metric(
        label="Today's Appointments",
        value=f"{today_appointments}",
        delta="Today"
    )

with col3:
    total_doctors = get_total_doctors()
    st.metric(
        label="Total Doctors",
        value=f"{total_doctors}",
        delta="Active"
    )

with col4:
    total_appointments = get_total_appointments()
    st.metric(
        label="Total Appointments",
        value=f"{total_appointments:,}",
        delta="All Time"
    )

st.markdown("---")

# 快速导航
st.subheader("Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("### Analytics\nView comprehensive analytics from hospital level to individual patients")
    if st.button("Go to Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")

with col2:
    st.info("### Predictions\nExplore predictive models for revenue and patient vitals")
    if st.button("Go to Predictions", use_container_width=True):
        st.switch_page("pages/predictions.py")

with col3:
    st.info("### Patient Management\nSearch and manage patient records")
    st.button("Go to Patients (Coming Soon)", use_container_width=True, disabled=True)

st.markdown("---")

# 系统信息
with st.expander("ℹ️ System Information"):
    st.write("**Database:** MySQL")
    st.write("**Framework:** Streamlit")
    st.write("**Version:** 1.0.0")
    st.write("**Last Updated:** 2024")

# 侧边栏
with st.sidebar:
    st.image(r"D:\NU\DS5110\final project\dashboard\images\icon.png", width=300)
    st.title("Navigation")
    st.markdown("---")
    
    st.subheader("📌 Available Pages")
    st.write("• 🏠 Home (Current)")
    st.write("• 📊 Analytics")
    st.write("• 🔮 Predictions")
    st.write("• 👥 Patients (Coming Soon)")
    
    st.markdown("---")
    st.caption("Hospital Management System v1.0")