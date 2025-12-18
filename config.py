import os
MysqlPasswd = os.getenv("MysqlPasswd")

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': MysqlPasswd,     # 使用环境变量
    'database': 'myhospitaldb',  # 你的数据库名
    'port': 3306
}

# Streamlit 页面配置
PAGE_CONFIG = {
    'page_title': 'Hospital Management System',
    'page_icon': '🏥',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# 颜色主题
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8'
}