import pandas as pd
import random

# Tạo dữ liệu ngẫu nhiên
num_samples = 50  # Số lượng bệnh nhân

data = {
    "Patient Id": [f"P{i+1}" for i in range(num_samples)],
    "Age": [random.randint(10, 80) for _ in range(num_samples)],
    "Gender": [random.choice([1, 2]) for _ in range(num_samples)],  # 1: Male, 2: Female
    "Air Pollution": [random.randint(1, 10) for _ in range(num_samples)],
    "Alcohol use": [random.randint(1, 10) for _ in range(num_samples)],
    "Dust Allergy": [random.randint(1, 10) for _ in range(num_samples)],
    "OccuPational Hazards": [random.randint(1, 10) for _ in range(num_samples)],
    "Genetic Risk": [random.randint(1, 10) for _ in range(num_samples)],
    "chronic Lung Disease": [random.randint(1, 10) for _ in range(num_samples)],
    "Balanced Diet": [random.randint(1, 10) for _ in range(num_samples)],
    "Obesity": [random.randint(1, 10) for _ in range(num_samples)],
    "Smoking": [random.randint(1, 10) for _ in range(num_samples)],
    "Passive Smoker": [random.randint(1, 10) for _ in range(num_samples)],
    "Chest Pain": [random.randint(1, 10) for _ in range(num_samples)],
    "Coughing of Blood": [random.randint(1, 10) for _ in range(num_samples)],
    "Fatigue": [random.randint(1, 10) for _ in range(num_samples)],
    "Weight Loss": [random.randint(1, 10) for _ in range(num_samples)],
    "Shortness of Breath": [random.randint(1, 10) for _ in range(num_samples)],
    "Wheezing": [random.randint(1, 10) for _ in range(num_samples)],
    "Swallowing Difficulty": [random.randint(1, 10) for _ in range(num_samples)],
    "Clubbing of Finger Nails": [random.randint(1, 10) for _ in range(num_samples)],
    "Frequent Cold": [random.randint(1, 10) for _ in range(num_samples)],
    "Dry Cough": [random.randint(1, 10) for _ in range(num_samples)],
    "Snoring": [random.randint(1, 10) for _ in range(num_samples)],
}

df = pd.DataFrame(data)

# Xuất ra file Excel
df.to_excel("sample_patient_data.xlsx", index=False)

print("✅ Đã tạo file sample_patient_data.xlsx thành công!")
