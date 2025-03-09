import pickle
import pandas as pd
import streamlit as st

# Load mô hình đã lưu
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Lấy danh sách cột mô hình đã học
expected_features = model.feature_names_in_

st.title("🎯 Dự đoán Level với RapidMiner")

st.write("Vui lòng nhập giá trị cho từng chỉ số:")

# Chia giao diện thành 2 cột
cols = st.columns(5)

# Lưu dữ liệu nhập
user_input = {}

# Hiển thị các input theo hàng ngang (2 cột)
for i, feature in enumerate(expected_features):
    with cols[i % 5]:  # Chia đều vào 2 cột
        user_input[feature] = st.number_input(f"{feature}", value=0.0)

# Khi nhấn nút dự đoán
if st.button("🚀 Dự đoán Level"):
    # Tạo DataFrame từ dữ liệu người dùng
    input_data = pd.DataFrame([user_input])  # Biến đổi thành DataFrame với một dòng

    # Dự đoán Level
    prediction = model.predict(input_data)[0]  # Lấy giá trị dự đoán

    # Hiển thị kết quả
    st.success(f"🎯 Kết quả dự đoán: {prediction}")
