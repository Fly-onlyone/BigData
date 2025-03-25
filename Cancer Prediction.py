import streamlit as st
import pandas as pd
import pickle
import uuid
from pyhive import hive

# Kết nối Hive
try:
    conn = hive.Connection(
        host="localhost", port=10000, username="hive", database="default"
    )
    cursor = conn.cursor()
    cursor.execute("USE cancer_db")
except Exception as e:
    st.error(f"Lỗi kết nối Hive: {e}")
    st.stop()

# ---------------- LOAD MODEL ----------------
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    expected_features = model.feature_names_in_
except Exception as e:
    st.error(f"Lỗi tải model: {str(e)}")
    st.stop()


# Hàm tạo patient_id tự động
def generate_patient_id():
    try:
        cursor.execute("SELECT patient_id FROM cancer_table")
        ids = [row[0] for row in cursor.fetchall()]

        # Lọc ra những ID hợp lệ (bắt đầu bằng 'P' và có số phía sau)
        numbers = [int(id[1:]) for id in ids if id.startswith("P") and id[1:].isdigit()]

        # Nếu không có ID nào, bắt đầu từ P001
        new_number = max(numbers) + 1 if numbers else 1
        return f"P{new_number:03d}"  # Định dạng luôn có 3 chữ số

    except Exception as e:
        print(f"Lỗi khi tạo patient_id: {e}")
        return "P001"

    # ================= PHẦN DỰ ĐOÁN =================


st.header("🎯 Dự đoán Level")
prediction_tab, stats_tab = st.tabs(["Dự đoán", "📊 Thống kê & Tìm kiếm"])

with prediction_tab:
    input_method = st.radio(
        "Chọn phương thức nhập liệu:",
        ["📋 Nhập thủ công", "📂 Tải file Excel"],
        horizontal=True,
    )

    if input_method == "📋 Nhập thủ công":
        cols = st.columns(2)
        user_input = {}

        with cols[0]:
            user_input["Age"] = st.number_input(
                "Tuổi", min_value=1, max_value=100, value=30, step=1
            )

        with cols[1]:
            gender_mapping = {"Nam": 1, "Nữ": 2}
            gender = st.selectbox("Giới tính", options=["Nam", "Nữ"], index=0)
            user_input["Gender"] = gender_mapping[gender]

        other_features = [f for f in expected_features if f not in ["Age", "Gender"]]
        cols_other = st.columns(3)
        for i, feature in enumerate(other_features):
            with cols_other[i % 3]:
                user_input[feature] = st.number_input(
                    f"{feature}", min_value=0, value=0, step=1, format="%d"
                )

        if st.button("🚀 Thực hiện dự đoán", use_container_width=True):
            input_data = pd.DataFrame([user_input])
            input_data = input_data.drop(columns=["Age", "Gender"], errors="ignore")

            try:
                prediction = model.predict(input_data)[0]
                st.success(f"**Kết quả dự đoán:** {prediction}")

                patient_id = generate_patient_id()

                save_df = input_data.copy()
                save_df["level"] = prediction
                save_df["gender"] = gender
                save_df["patient_id"] = patient_id

                try:
                    for _, row in save_df.iterrows():
                        # Chuyển đổi giá trị thành đúng định dạng của Hive
                        values = ", ".join(
                            [f"'{x}'" if isinstance(x, str) else str(x) for x in row]
                        )

                        # Đảm bảo cột khớp với bảng Hive
                        column_names = ", ".join(save_df.columns)

                        # Fix lỗi 'gender' không có trong bảng Hive
                        if "gender" not in column_names.lower():
                            column_names = column_names.replace("gender", "Gender")

                        # Thực hiện câu lệnh INSERT
                        insert_query = f"INSERT INTO cancer_table ({column_names}) VALUES ({values})"
                        st.write(f"📌 Debug SQL: {insert_query}")  # Debug câu lệnh SQL
                        cursor.execute(insert_query)

                    conn.commit()
                    st.success(
                        f"✅ Dữ liệu đã lưu vào Hive với patient_id: {patient_id}"
                    )

                except Exception as e:
                    st.error(f"Lỗi lưu dữ liệu vào Hive: {e}")

            except Exception as e:
                st.error(f"Lỗi dự đoán: {str(e)}")


# ================= PHẦN THỐNG KÊ & TÌM KIẾM =================
st.subheader("📊 Thống kê & Tìm kiếm dữ liệu")


def fetch_hive_data():
    try:
        query = "SELECT * FROM cancer_table"
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    except Exception as e:
        st.error(f"Lỗi lấy dữ liệu từ Hive: {e}")
        return pd.DataFrame()


# Nút làm mới dữ liệu
if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
    st.session_state["df_history"] = fetch_hive_data()
    st.rerun()

if "df_history" not in st.session_state:
    st.session_state["df_history"] = fetch_hive_data()

df_history = st.session_state["df_history"]

if not df_history.empty:
    if "Age" in df_history.columns and pd.api.types.is_numeric_dtype(df_history["Age"]):
        age_min = int(df_history["Age"].min())
        age_max = int(df_history["Age"].max())
        col_age1, col_age2 = st.columns(2)
        age_from = col_age1.number_input(
            "Tuổi (nhỏ nhất)",
            min_value=age_min,
            max_value=age_max,
            value=age_min,
            step=1,
        )
        age_to_val = col_age2.number_input(
            "Tuổi (lớn nhất)",
            min_value=age_min,
            max_value=age_max,
            value=age_max,
            step=1,
        )
    else:
        age_from, age_to_val = None, None

    if "Gender" in df_history.columns:
        gender_options = sorted(df_history["Gender"].dropna().unique().tolist())
        gender_filter = st.multiselect(
            "Chọn giới tính:", gender_options, default=gender_options
        )
    else:
        gender_filter = None

    filtered_df = df_history.copy()
    if age_from is not None and age_to_val is not None:
        filtered_df = filtered_df[
            (filtered_df["Age"] >= age_from) & (filtered_df["Age"] <= age_to_val)
        ]
    if gender_filter:
        filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]

    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("📌 Chưa có dữ liệu dự đoán nào!")
