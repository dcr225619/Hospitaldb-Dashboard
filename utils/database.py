import mysql.connector
import pandas as pd
import streamlit as st
from config import DB_CONFIG

def get_connection():
    """创建数据库连接（缓存以提高性能）"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl=300)  # 缓存5分钟
def run_query(query, params=None):
    """执行查询并返回 DataFrame"""
    conn = get_connection()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None
    finally:
        if conn.is_connected():
            conn.close()

def execute_query(query, params=None):
    """执行非查询语句（INSERT, UPDATE, DELETE）"""
    conn = get_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            conn.close()

def test_connection():
    """测试数据库连接"""
    conn = get_connection()
    if conn and conn.is_connected():
        return True
    return False