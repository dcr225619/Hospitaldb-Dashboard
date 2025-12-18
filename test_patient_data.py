# test_patient_data.py
# 测试哪些患者在 patient_labs 中有数据

import sys
sys.path.append('.')  # 添加当前目录到路径

from utils.database import run_query
from utils.queries import get_patient_blood_chemistry, get_patient_vitamin_levels, search_patients
import pandas as pd

def test_all_patients():
    """测试所有患者的实验室数据"""
    
    print("=" * 80)
    print("Testing Patient Lab Data Availability")
    print("=" * 80)
    
    # 1. 获取所有患者
    query = """
    SELECT 
        `Patient ID` as patient_id,
        CONCAT(`First Name`, ' ', `Last Name`) as full_name,
        `Gender` as gender,
        `DOB` as dob
    FROM patients
    ORDER BY `Patient ID`
    LIMIT 50
    """
    
    all_patients = run_query(query)
    
    if all_patients is None or all_patients.empty:
        print("❌ No patients found in database!")
        return
    
    print(f"\n✅ Found {len(all_patients)} patients in database")
    print("\nTesting each patient for lab data...\n")
    
    # 2. 测试每个患者
    patients_with_blood_data = []
    patients_with_vitamin_data = []
    patients_with_no_data = []
    
    for idx, patient in all_patients.iterrows():
        patient_id = int(patient['patient_id'])
        patient_name = patient['full_name']
        
        # 测试血液化学数据
        blood_data = get_patient_blood_chemistry(patient_id)
        has_blood = blood_data is not None and not blood_data.empty
        
        # 测试维生素数据
        vitamin_data = get_patient_vitamin_levels(patient_id)
        has_vitamin = vitamin_data is not None and not vitamin_data.empty
        
        # 统计
        if has_blood or has_vitamin:
            if has_blood:
                blood_count = len(blood_data)
                # 检查有数据的列
                blood_cols = blood_data.notna().sum()
                blood_cols_with_data = [col for col in blood_cols.index if blood_cols[col] > 0 and col != 'date_of_visit']
            else:
                blood_count = 0
                blood_cols_with_data = []
            
            if has_vitamin:
                vitamin_count = len(vitamin_data)
                vitamin_cols = vitamin_data.notna().sum()
                vitamin_cols_with_data = [col for col in vitamin_cols.index if vitamin_cols[col] > 0 and col != 'date_of_visit']
            else:
                vitamin_count = 0
                vitamin_cols_with_data = []
            
            # 记录
            if has_blood:
                patients_with_blood_data.append({
                    'patient_id': patient_id,
                    'name': patient_name,
                    'record_count': blood_count,
                    'columns_with_data': ', '.join(blood_cols_with_data)
                })
            
            if has_vitamin:
                patients_with_vitamin_data.append({
                    'patient_id': patient_id,
                    'name': patient_name,
                    'record_count': vitamin_count,
                    'columns_with_data': ', '.join(vitamin_cols_with_data)
                })
            
            print(f"✅ Patient {patient_id:3d} - {patient_name:30s} | Blood: {blood_count:2d} records | Vitamin: {vitamin_count:2d} records")
        else:
            patients_with_no_data.append({
                'patient_id': patient_id,
                'name': patient_name
            })
            print(f"❌ Patient {patient_id:3d} - {patient_name:30s} | No data")
    
    # 3. 总结报告
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  - Total patients tested: {len(all_patients)}")
    print(f"  - Patients with blood chemistry data: {len(patients_with_blood_data)}")
    print(f"  - Patients with vitamin D data: {len(patients_with_vitamin_data)}")
    print(f"  - Patients with no lab data: {len(patients_with_no_data)}")
    
    # 4. 详细列表 - 有血液化学数据的患者
    if patients_with_blood_data:
        print(f"\n🩸 Patients with Blood Chemistry Data ({len(patients_with_blood_data)}):")
        print("-" * 80)
        blood_df = pd.DataFrame(patients_with_blood_data)
        print(blood_df.to_string(index=False))
    
    # 5. 详细列表 - 有维生素数据的患者
    if patients_with_vitamin_data:
        print(f"\n💊 Patients with Vitamin D Data ({len(patients_with_vitamin_data)}):")
        print("-" * 80)
        vitamin_df = pd.DataFrame(patients_with_vitamin_data)
        print(vitamin_df.to_string(index=False))
    
    # 6. 推荐测试患者
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDED PATIENTS FOR TESTING")
    print("=" * 80)
    
    if patients_with_blood_data:
        print("\n✨ Best patients to test Blood Chemistry Panel:")
        for i, patient in enumerate(patients_with_blood_data[:5], 1):
            print(f"  {i}. Patient ID: {patient['patient_id']} - {patient['name']}")
            print(f"     Records: {patient['record_count']} | Columns: {patient['columns_with_data']}")
    
    if patients_with_vitamin_data:
        print("\n✨ Best patients to test Vitamin D Levels:")
        for i, patient in enumerate(patients_with_vitamin_data[:5], 1):
            print(f"  {i}. Patient ID: {patient['patient_id']} - {patient['name']}")
            print(f"     Records: {patient['record_count']} | Columns: {patient['columns_with_data']}")
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_all_patients()