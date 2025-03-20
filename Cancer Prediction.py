import streamlit as st
import pandas as pd
import pickle
import io

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

    st.write("Vui lòng chọn cách nhập dữ liệu:")

    # Tabs: Nhập tay hoặc Upload file
    tab1, tab2 = st.tabs(["📋 Nhập tay", "📂 Tải file .xlsx"])

    # === Tab Nhập tay ===
    with tab1:
        st.write("Vui lòng nhập giá trị cho từng chỉ số:")

        cols = st.columns(5)
        user_input = {}

        for i, feature in enumerate(expected_features):
            with cols[i % 5]:
                user_input[feature] = st.number_input(f"{feature}", value=0.0)

        if st.button("🚀 Dự đoán từ nhập tay"):
            input_data = pd.DataFrame([user_input])

            # Dự đoán Level
            prediction = model.predict(input_data)[0]

            st.success(f"🎯 Kết quả dự đoán: {prediction}")

    # === Tab Upload file ===
    with tab2:
        st.write("Tải lên file Excel (.xlsx) có định dạng phù hợp:")

        uploaded_file = st.file_uploader("📂 Chọn file .xlsx", type=["xlsx"])

        if uploaded_file is not None:
            try:
                df_input = pd.read_excel(uploaded_file)

                # Tiền xử lý: chuẩn hóa tên cột giống với model
                df_input.columns = [col.strip().replace(" ", "_") for col in df_input.columns]

                # Kiểm tra thiếu cột
                missing_cols = set(expected_features) - set(df_input.columns)
                if missing_cols:
                    st.error(f"⚠️ Thiếu các cột sau trong file: {', '.join(missing_cols)}")
                else:
                    st.write("📄 Dữ liệu đã tải lên:")
                    st.dataframe(df_input)

                    # Lọc đúng các cột model cần
                    model_input = df_input[expected_features]

                    if st.button("🚀 Dự đoán từ file"):
                        predictions = model.predict(model_input)
                        df_input['Dự đoán Level'] = predictions

                        st.success("✅ Dự đoán thành công!")
                        st.write(df_input)

                        # Xuất file kết quả vào bộ nhớ
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_input.to_excel(writer, index=False)
                        output.seek(0)

                        # Nút tải file
                        st.download_button(
                            label="📥 Tải kết quả về (.xlsx)",
                            data=output,
                            file_name="prediction_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            except Exception as e:
                st.error(f"❌ Lỗi khi đọc file: {e}")

