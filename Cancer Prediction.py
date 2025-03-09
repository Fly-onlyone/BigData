import pickle
import pandas as pd
import streamlit as st

# Load mô hình đã lưu
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Lấy danh sách cột mô hình đã học
expected_features = model.feature_names_in_

# Tạo sidebar để chọn màn hình
st.sidebar.title("🔍 Chọn màn hình")
screen = st.sidebar.radio("Điều hướng", ["Dự đoán", "Thống kê & Tìm kiếm"])

if screen == "Dự đoán":
    st.title("🎯 Dự đoán Level với RapidMiner")

    st.write("Vui lòng nhập giá trị cho từng chỉ số:")

    # Chia giao diện thành nhiều cột
    cols = st.columns(5)

    # Lưu dữ liệu nhập
    user_input = {}

    # Hiển thị các input theo hàng ngang
    for i, feature in enumerate(expected_features):
        with cols[i % 5]:
            user_input[feature] = st.number_input(f"{feature}", value=0.0)

    # Khi nhấn nút dự đoán
    if st.button("🚀 Dự đoán Level"):
        # Tạo DataFrame từ dữ liệu người dùng
        input_data = pd.DataFrame([user_input])

        # Dự đoán Level
        prediction = model.predict(input_data)[0]

        # Hiển thị kết quả
        st.success(f"🎯 Kết quả dự đoán: {prediction}")

elif screen == "Thống kê & Tìm kiếm":
    st.title("📊 Thống kê & Lọc bệnh nhân")

    try:
        # Đọc dữ liệu
        df = pd.read_csv("unlabeled_data.csv")

        if df.empty:
            st.error("❌ Dữ liệu trống! Hãy thực hiện dự đoán trước.")
        else:
            # Loại bỏ cột không phải số
            numeric_df = df.select_dtypes(include=['number'])

            # Hiển thị thống kê mô tả
            st.write("### 📌 Thống kê mô tả")
            st.write(numeric_df.describe())

            # Hiển thị biểu đồ phân phối
            if not numeric_df.empty:
                st.write("### 📊 Biểu đồ phân phối")
                st.bar_chart(numeric_df)
            else:
                st.warning("⚠ Không có dữ liệu số để hiển thị biểu đồ!")

            # Bộ lọc dữ liệu
            st.write("### 🔍 Tìm kiếm bệnh nhân theo chỉ số")

            # Chia giao diện thành 5 cột cho các bộ lọc
            filter_cols = st.columns(5)
            filters = {}

            for i, feature in enumerate(numeric_df.columns):
                with filter_cols[i % 5]:
                    min_val, max_val = float(df[feature].min()), float(df[feature].max())
                    filters[feature] = st.slider(f"{feature}", min_val, max_val, (min_val, max_val))

            # Lọc dữ liệu dựa trên giá trị nhập vào slider
            filtered_df = df.copy()
            for feature, (min_val, max_val) in filters.items():
                filtered_df = filtered_df[(filtered_df[feature] >= min_val) & (filtered_df[feature] <= max_val)]

            # Hiển thị kết quả lọc
            st.write(f"### 🏥 Kết quả lọc ({len(filtered_df)} bệnh nhân)")
            st.dataframe(filtered_df)

    except FileNotFoundError:
        st.error("❌ Không tìm thấy dữ liệu! Hãy thực hiện dự đoán trước.")
