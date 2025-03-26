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
    expected_features = model.feature_names_in_
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
        cols = st.columns(2)
        user_input = {}

        with cols[0]:
            user_input["Age"] = st.number_input(
                "Tuổi", min_value=1, max_value=100, value=30, step=1
            )
        with cols[1]:
            gender_mapping = {"Nam": 1, "Nữ": 2}
            gender_text = st.selectbox("Giới tính", options=["Nam", "Nữ"], index=0)
            user_input["Gender"] = gender_mapping[gender_text]

        # Build user input for prediction: assume expected_features excludes "Age" and "Gender"
        # (if they are used in prediction, adjust accordingly)
        other_features = [f for f in expected_features if f not in ["Age", "Gender"]]
        for feature in other_features:
            user_input[feature] = st.number_input(
                f"{feature}", min_value=0, value=0, step=1
            )

        if st.button("🚀 Thực hiện dự đoán", use_container_width=True):
            # Create a DataFrame with all input values
            input_data = pd.DataFrame([user_input])
            # Rename keys to lowercase for consistency with Hive table schema
            input_data.rename(columns={"Age": "age", "Gender": "gender"}, inplace=True)

            try:
                # Use only the features needed for prediction
                features_for_pred = input_data[
                    [f for f in input_data.columns if f in other_features]
                ]
                prediction = model.predict(features_for_pred)[0]
                st.success(f"**Kết quả dự đoán:** {prediction}")

                patient_id = generate_patient_id()

                # Expected table columns in the correct order:
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

                # Build a dictionary with values from input_data and defaults for missing columns.
                insert_data = {}
                # For columns that come from user input:
                # age and gender are provided; other features might or might not be provided.
                for col in expected_columns:
                    if col == "patient_id":
                        insert_data[col] = patient_id
                    elif col == "level":
                        insert_data[col] = prediction
                    elif col in input_data.columns:
                        insert_data[col] = input_data[col].iloc[0]
                    else:
                        # Set default value: numeric columns default to 0, string columns to empty.
                        # Here we assume columns except patient_id and level are numeric.
                        insert_data[col] = 0

                # Convert dictionary to DataFrame ensuring the column order:
                save_df = pd.DataFrame([insert_data], columns=expected_columns)

                # Build INSERT statement:
                columns_str = ", ".join(expected_columns)
                # Create a comma-separated list of values, wrapping strings in single quotes.
                # For simplicity, we assume all values are either numeric or strings.
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
                st.write(f"📌 Debug SQL: {insert_query}")  # Debug output
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
    st.rerun()

if "df_history" not in st.session_state:
    st.session_state["df_history"] = fetch_hive_data()

df_history = st.session_state["df_history"]

if not df_history.empty:
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

    if "gender" in df_history.columns:
        gender_options = sorted(df_history["gender"].dropna().unique().tolist())
        gender_filter = st.multiselect(
            "Chọn giới tính:", gender_options, default=gender_options
        )
    else:
        gender_filter = None

    filtered_df = df_history.copy()
    if age_from is not None and age_to_val is not None:
        filtered_df = filtered_df[
            (filtered_df["age"] >= age_from) & (filtered_df["age"] <= age_to_val)
        ]
    if gender_filter:
        filtered_df = filtered_df[filtered_df["gender"].isin(gender_filter)]

    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("📌 Chưa có dữ liệu dự đoán nào!")

# Close Hive connection when done (optional if you want to allow further interactions)
# cursor.close()
# conn.close()
