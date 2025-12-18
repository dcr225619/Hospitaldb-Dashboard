from .database import run_query
import pandas as pd

def get_most_visited_hospitals():
    """get top 10 hospitals with most visit volumns"""
    query = """
    SELECT h.hospital_name,
        COUNT(DISTINCT a.appointment_id) as visit_count
    FROM hospitals h
    LEFT JOIN departments d ON h.hospital_id = d.hospital_id
    LEFT JOIN doctors do ON d.department_id = do.department_id
    LEFT JOIN appointments a ON a.doctor_id = do.doctor_id
    GROUP BY h.hospital_id, h.hospital_name
    ORDER BY visit_count DESC
    LIMIT 10
    """
    return run_query(query)

def get_most_visited_departments():
    """get top 10 departments with most visit volumns"""
    query = """
        SELECT dp.department_name, h.hospital_name, count(*) as frequency
        FROM appointments a
        LEFT JOIN doctors d
        ON a.doctor_id = d.doctor_id
        LEFT JOIN departments dp
        ON d.department_id = dp.department_id
        LEFT JOIN hospitals h
        ON dp.hospital_id = h.hospital_id
        GROUP BY d.department_id
        ORDER BY frequency DESC
        LIMIT 10
    """
    return run_query(query)

def get_department_patient_doctor_ratio():
    """get top 10 departments with highest patient_doctor ratio"""
    query = """
        SELECT dc.hospital_name, dc.department_name, count(*) as patient_count, dc.doctor_num as doctor_count,
            count(*) / dc.doctor_num as patient_doctor_ratio
        FROM appointments a
        LEFT JOIN doctors d on a.doctor_id = d.doctor_id
        LEFT JOIN doctorcount dc on d.department_id = dc.department_id
        GROUP BY dc.department_id, dc.doctor_num
        ORDER BY patient_doctor_ratio desc
        LIMIT 10
    """
    return run_query(query)

def get_monthly_appointment_trend():
    """get monthly appointment trend in the data"""
    query = """
        SELECT MONTH(appointment_date) as 'month', count(*) as appointment_num
        FROM appointments
        GROUP BY MONTH(appointment_date)
        ORDER BY MONTH(appointment_date)
    """
    return run_query(query)

def get_appointment_status_ratio():
    """get appointment status summary """
    query = """
        SELECT sum(if(status = 'Scheduled', 1, 0)) / count(*) as scheduled, sum(if(status = 'Cancelled', 1, 0)) / count(*) as cancelled,
        sum(if(status = 'Completed', 1, 0)) / count(*) as completed
        FROM appointments
    """
    return run_query(query)

def get_patient_age_groups():
    """get patient age distribution"""
    query = """
    SELECT 
        CASE 
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 10 THEN '0-9'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 20 THEN '10-19'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 30 THEN '20-29'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 40 THEN '30-39'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 50 THEN '40-49'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 60 THEN '50-59'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 70 THEN '60-69'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 80 THEN '70-79'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 90 THEN '80-89'
            ELSE '90+'
        END as age_group,
        COUNT(*) as count
    FROM patients
    GROUP BY age_group
    ORDER BY age_group
    """
    return run_query(query)

def get_patient_age_gender_distribution():
    """get patient age-gender distribution"""
    query = """
    SELECT 
        gender,
        CASE 
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 18 THEN '0-17'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 30 THEN '18-29'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 45 THEN '30-44'
            WHEN YEAR(CURDATE()) - YEAR(date_of_birth) < 60 THEN '45-59'
            ELSE '60+'
        END as age_group,
        COUNT(*) as count
    FROM patients
    GROUP BY gender, age_group
    ORDER BY gender, age_group
    """
    return run_query(query)

def get_hospital_avg_rating():
    """get hospital ratings"""
    query = """
    SELECT h.hospital_name, AVG(d.doctor_rating) as avg_rating
    FROM doctors d
    LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
    GROUP BY h.hospital_name
    ORDER BY avg_rating DESC
    """
    return run_query(query)

def get_patient_age_by_hospital_for_boxplot():
    """get patient age distribution for each hospital """
    query = """
    SELECT
        h.hospital_name,
        YEAR(CURDATE()) - YEAR(p.date_of_birth) as age
    FROM patients p
    JOIN appointments a ON p.patient_id = a.patient_id
    LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
    LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
    WHERE h.hospital_name IS NOT NULL
    ORDER BY h.hospital_name, age
    """
    return run_query(query)

# ==================== Vital Signs Analytics ====================

def get_weight_height_by_gender():
    """按性别获取体重和身高数据"""
    query = """
    SELECT 
        p.gender,
        pv.weight,
        pv.height
    FROM patient_vitals pv
    JOIN patients p ON pv.patient_id = p.patient_id
    WHERE pv.weight IS NOT NULL AND pv.height IS NOT NULL
    """
    return run_query(query)

def get_bmi_by_gender():
    """计算并获取 BMI 数据"""
    query = """
    SELECT 
        p.gender,
        ROUND(pv.weight / ((pv.height/100) * (pv.height/100)), 2) as bmi
    FROM patient_vitals pv
    JOIN patients p ON pv.patient_id = p.patient_id
    WHERE pv.weight IS NOT NULL 
      AND pv.height IS NOT NULL
      AND pv.height > 0
    """
    return run_query(query)

# ==================== Laboratory Analytics ====================

def get_hormone_distribution_by_gender():
    """按性别获取激素分布"""
    query = """
    SELECT 
        p.gender,
        pl.tsh,
        pl.t3,
        pl.hemoglobin
    FROM patient_labs pl
    JOIN patients p ON pl.patient_id = p.patient_id
    WHERE pl.tsh IS NOT NULL 
       OR pl.t3 IS NOT NULL 
       OR pl.hemoglobin IS NOT NULL
    """
    return run_query(query)

# ==================== Individual Patient Tracking ====================

def search_patients(search_term):
    """
    搜索患者（支持模糊搜索，不区分大小写）
    
    Parameters:
    -----------
    search_term : str
        搜索关键词（可以是名、姓、全名或邮箱的一部分）
    
    Returns:
    --------
    pandas.DataFrame with patient information
    """
    query = """
    SELECT 
        patient_id,
        CONCAT(first_name, ' ', last_name) as 'full_name',
        first_name,
        last_name,
        gender,
        DATE_FORMAT(date_of_birth, '%Y-%m-%d') as 'date_of_birth',
        contact_number,
        email
    FROM patients
    WHERE LOWER(first_name) LIKE LOWER(%s)
       OR LOWER(last_name) LIKE LOWER(%s)
       OR LOWER(email) LIKE LOWER(%s)
       OR LOWER(CONCAT(first_name, ' ', last_name)) LIKE LOWER(%s)
    ORDER BY last_name, first_name
    LIMIT 20
    """
    # 在搜索词前后添加通配符 %
    search_pattern = f"%{search_term}%"
    return run_query(query, params=(search_pattern, search_pattern, search_pattern, search_pattern))


def get_patient_blood_chemistry(patient_id):
    """获取患者血液化学指标时间序列"""
    query = """
    SELECT 
        date_of_visit,
        total_cholesterol,
        ldl,
        hdl,
        triglycerides,
        hemoglobin,
        wbc,
        rbc,
        platelets
    FROM patient_labs
    WHERE patient_id = %s
    ORDER BY date_of_visit
    """
    df = run_query(query, params=(patient_id,))

    if df is not None and not df.empty:
        numeric_cols = ['total_cholesterol', 'ldl', 'hdl', 'triglycerides', 
                        'hemoglobin', 'wbc', 'rbc', 'platelets']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def get_patient_vitamin_levels(patient_id):
    """获取患者维生素水平时间序列"""
    query = """
    SELECT 
        date_of_visit,
        vitamin_d2,
        vitamin_d3,
        vitamin_d_total
    FROM patient_labs
    WHERE patient_id = %s
    ORDER BY date_of_visit
    """

    df = run_query(query, params=(patient_id,))
    
    if df is not None and not df.empty:
        numeric_cols = ['vitamin_d2', 'vitamin_d3', 'vitamin_d_total']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


# ==================== Dashboard KPIs ====================

def get_total_patients():
    """get total num of patients"""
    query = "SELECT COUNT(*) as count FROM patients"
    result = run_query(query)
    return result['count'][0] if result is not None and len(result) > 0 else 0

def get_total_appointments():
    """get total num of appointments"""
    query = "SELECT COUNT(*) as count FROM appointments"
    result = run_query(query)
    return result['count'][0] if result is not None and len(result) > 0 else 0

def get_total_doctors():
    """get total num of doctors"""
    query = "SELECT COUNT(*) as count FROM doctors"
    result = run_query(query)
    return result['count'][0] if result is not None and len(result) > 0 else 0

def get_today_appointments():
    """get total num of appointments today"""
    query = """
    SELECT COUNT(*) as count 
    FROM appointments 
    WHERE DATE(appointment_date) = CURDATE()
    """
    result = run_query(query)
    return result['count'][0] if result is not None and len(result) > 0 else 0

# ==================== Prediction ====================

def get_hospital_revenue_history():
    """获取医院收入历史数据用于预测"""
    query = """
    SELECT 
        d.hospital_id,
        DATE_FORMAT(b.bill_date, '%Y-%m') AS 'year_month',
        SUM(b.amount) AS amount
    FROM billing b
    INNER JOIN treatments t ON b.treatment_id = t.treatment_id
    INNER JOIN appointments a ON t.appointment_id = a.appointment_id
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE b.payment_status = 'Paid'
    GROUP BY d.hospital_id, DATE_FORMAT(b.bill_date, '%Y-%m')
    ORDER BY d.hospital_id, DATE_FORMAT(b.bill_date, '%Y-%m')
    """
    return run_query(query)