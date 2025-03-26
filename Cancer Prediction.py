import streamlit as st
import pandas as pd
import pickle
from pyhive import hive

# Kết nối đến Hive
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
    # You can define the exact order of features here, including snoring's position
    # If your model has a certain order, you can reorder them below as needed:
    custom_feature_order = [
        "air_pollution",
        "alcohol_use",
        "dust_allergy",
        "occupational_hazards",
        "genetic_risk",
        "chronic_lung_disease",
        "balanced_diet",
        "obesity",
        "smoking",
        "passive_smoker",
        "chest_pain",
        "coughing_of_blood",
        "fatigue",
        "weight_loss",
        "shortness_of_breath",
        "wheezing",
        "swallowing_difficulty",
        "clubbing_of_finger_nails",
        "frequent_cold",
        "dry_cough",
        "snoring",
    ]
    # If your model enforces a strict set of features, cross-check with model.feature_names_in_:
    expected_features = [
        f for f in custom_feature_order if f in model.feature_names_in_
    ]
except Exception as e:
    st.error(f"Lỗi tải model: {str(e)}")
    st.stop()


# Hàm tạo patient_id tự động
def generate_patient_id():
    try:
        cursor.execute("SELECT patient_id FROM cancer_table")
        ids = [row[0] for row in cursor.fetchall()]
        numbers = [
            int(pid[1:]) for pid in ids if pid.startswith("P") and pid[1:].isdigit()
        ]
        new_number = max(numbers) + 1 if numbers else 1
        return f"P{new_number:03d}"
    except Exception as e:
        st.error(f"Lỗi khi tạo patient_id: {e}")
        return "P001"


st.header("🎯 Dự đoán Level")
prediction_tab, stats_tab = st.tabs(["Dự đoán", "📊 Thống kê & Tìm kiếm dữ liệu"])

with prediction_tab:
    input_method = st.radio(
        "Chọn phương thức nhập liệu:",
        ["📋 Nhập thủ công", "📂 Tải file Excel"],
        horizontal=True,
    )

    if input_method == "📋 Nhập thủ công":
        # Nhập cột Age và Gender
        col1, col2 = st.columns(2)
        user_input = {}

        with col1:
            user_input["Age"] = st.number_input(
                "Tuổi", min_value=1, max_value=100, value=30, step=1
            )
        with col2:
            gender_mapping = {"Nam": 1, "Nữ": 2}
            gender_text = st.selectbox("Giới tính", options=["Nam", "Nữ"], index=0)
            user_input["Gender"] = gender_mapping[gender_text]

        # Lấy danh sách feature trừ Age và Gender
        other_features = [f for f in expected_features if f not in ["Age", "Gender"]]

        # Chia thành các nhóm 5 cột mỗi hàng
        num_cols = 5
        # Tạo danh sách các chunk 5 phần tử
        feature_chunks = [
            other_features[i : i + num_cols]
            for i in range(0, len(other_features), num_cols)
        ]

        # Render input theo hàng x cột
        for chunk in feature_chunks:
            cols_chunk = st.columns(len(chunk))  # Mỗi chunk có len(chunk) cột
            for i, feature in enumerate(chunk):
                user_input[feature] = cols_chunk[i].number_input(
                    feature, min_value=0, value=0, step=1
                )

        # Nút dự đoán
        if st.button("🚀 Thực hiện dự đoán", use_container_width=True):
            # Tạo DataFrame
            input_data = pd.DataFrame([user_input])
            # Đổi tên cột cho khớp với bảng Hive (lowercase)
            input_data.rename(columns={"Age": "age", "Gender": "gender"}, inplace=True)

            try:
                # Chọn cột để predict
                features_for_pred = input_data[
                    [f for f in input_data.columns if f in other_features]
                ]
                prediction = model.predict(features_for_pred)[0]
                st.success(f"**Kết quả dự đoán:** {prediction}")

                patient_id = generate_patient_id()

                # Danh sách cột theo thứ tự trong bảng Hive
                expected_columns = [
                    "patient_id",
                    "age",
                    "gender",
                    "air_pollution",
                    "alcohol_use",
                    "dust_allergy",
                    "occupational_hazards",
                    "genetic_risk",
                    "chronic_lung_disease",
                    "balanced_diet",
                    "obesity",
                    "smoking",
                    "passive_smoker",
                    "chest_pain",
                    "coughing_of_blood",
                    "fatigue",
                    "weight_loss",
                    "shortness_of_breath",
                    "wheezing",
                    "swallowing_difficulty",
                    "clubbing_of_finger_nails",
                    "frequent_cold",
                    "dry_cough",
                    "snoring",
                    "level",
                ]

                # Tạo dict để insert
                insert_data = {}
                for col in expected_columns:
                    if col == "patient_id":
                        insert_data[col] = patient_id
                    elif col == "level":
                        insert_data[col] = prediction
                    elif col in input_data.columns:
                        insert_data[col] = input_data[col].iloc[0]
                    else:
                        # Mặc định: cột số = 0, cột chuỗi = ""
                        insert_data[col] = 0

                # Tạo DataFrame final
                save_df = pd.DataFrame([insert_data], columns=expected_columns)

                # Build INSERT statement
                columns_str = ", ".join(expected_columns)
                values = ", ".join(
                    [
                        (
                            f"'{str(x).replace(chr(39), chr(39)*2)}'"
                            if isinstance(x, str)
                            else str(x)
                        )
                        for x in save_df.iloc[0]
                    ]
                )
                insert_query = (
                    f"INSERT INTO cancer_table ({columns_str}) VALUES ({values})"
                )
                st.write(f"📌 Debug SQL: {insert_query}")
                cursor.execute(insert_query)
                conn.commit()
                st.success(f"✅ Dữ liệu đã lưu vào Hive với patient_id: {patient_id}")
            except Exception as e:
                st.error(f"Lỗi dự đoán hoặc lưu dữ liệu: {str(e)}")


# ---------------- PHẦN THỐNG KÊ & TÌM KIẾM ----------------
st.subheader("📊 Thống kê & Tìm kiếm dữ liệu")


def fetch_hive_data():
    try:
        cursor.execute("SELECT * FROM cancer_table")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Lỗi lấy dữ liệu từ Hive: {e}")
        return pd.DataFrame()


if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
    st.session_state["df_history"] = fetch_hive_data()
    st.experimental_rerun()

if "df_history" not in st.session_state:
    st.session_state["df_history"] = fetch_hive_data()

df_history = st.session_state["df_history"]

if not df_history.empty:
    # Lọc theo tuổi
    if "age" in df_history.columns and pd.api.types.is_numeric_dtype(df_history["age"]):
        age_min = int(df_history["age"].min())
        age_max = int(df_history["age"].max())
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

    # Lọc theo giới tính
    if "gender" in df_history.columns:
        gender_options = sorted(df_history["gender"].dropna().unique().tolist())
        gender_filter = st.multiselect(
            "Chọn giới tính:", gender_options, default=gender_options
        )
    else:
        gender_filter = None

    # Áp dụng bộ lọc
    filtered_df = df_history.copy()
    if age_from is not None and age_to_val is not None:
        filtered_df = filtered_df[
            (filtered_df["age"] >= age_from) & (filtered_df["age"] <= age_to_val)
        ]
    if gender_filter:
        filtered_df = filtered_df[filtered_df["gender"].isin(gender_filter)]

    st.dataframe(filtered_df, use_container_width=True)

    # Hiển thị biểu đồ cột (bar chart) theo level
    if "level" in filtered_df.columns:
        level_counts = filtered_df["level"].value_counts().reset_index()
        level_counts.columns = ["level", "count"]
        st.bar_chart(data=level_counts.set_index("level"))
else:
    st.warning("📌 Chưa có dữ liệu dự đoán nào!")
