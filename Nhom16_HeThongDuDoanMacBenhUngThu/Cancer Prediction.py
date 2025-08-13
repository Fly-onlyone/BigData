import pickle

import altair as alt
import pandas as pd
import streamlit as st
from pyhive import hive

# KẾT NỐI HIVE
try:
    conn = hive.Connection(
        host="localhost", port=10000, username="hive", database="default"
    )
    cursor = conn.cursor()
    cursor.execute("USE cancer_db")
except Exception as e:
    st.error(f"Lỗi kết nối Hive: {e}")
    st.stop()

# LOAD MODEL
try:
    with open("model/model.pkl", "rb") as f:
        model = pickle.load(f)
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
    # expected_features dùng cho dự đoán
    expected_features = [
        f for f in custom_feature_order if f in model.feature_names_in_
    ]
except Exception as e:
    st.error(f"Lỗi tải model: {str(e)}")
    st.stop()


# HÀM TẠO PATIENT_ID
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


# HÀM MAP PREDICTION
def map_prediction(pred):
    mapping = {0: "Low", 1: "Medium", 2: "High"}
    return mapping.get(pred, "Unknown")


# GIAO DIỆN CHÍNH
st.title("Ứng dụng Dự đoán và Thống kê")

# HIỂN THỊ DỮ LIỆU DỰ ĐOÁN BAN ĐẦU
st.markdown("## 📋 Xem Dữ Liệu Dự Đoán Ban Đầu")

if st.button("📂 Hiển thị dữ liệu", key="show_predicted_data"):
    try:
        df_predicted = pd.read_excel("data/predictions.xlsx", engine="openpyxl")

        # Chuẩn hóa tên cột nếu cần
        df_predicted.columns = [
            col.strip().lower().replace(" ", "_") for col in df_predicted.columns
        ]

        st.dataframe(df_predicted, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")


st.markdown("## Phần Dự đoán")
st.write("📂 Tải file Excel")

# 1) TẢI FILE EXCEL
st.info(
    """
    **Hướng dẫn tạo file Excel:**
    - Tạo file Excel (.xlsx hoặc .xls) chứa dữ liệu của bệnh nhân.
    - Các cột cần có:
        - **Age**: tuổi của bệnh nhân (số nguyên).
        - **Gender**: giới tính của bệnh nhân (ví dụ: "Nam" hoặc "Nữ").
        - Các cột thuộc tính (features): 
          `air_pollution, alcohol_use, dust_allergy, occupational_hazards, genetic_risk, chronic_lung_disease, balanced_diet, obesity, smoking, passive_smoker, chest_pain, coughing_of_blood, fatigue, weight_loss, shortness_of_breath, wheezing, swallowing_difficulty, clubbing_of_finger_nails, frequent_cold, dry_cough, snoring`
    - Nếu file Excel có cột "Patient Id" hoặc "patient_id", nó sẽ bị loại bỏ.
    """
)
uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"])
if uploaded_file is not None:
    try:
        excel_df = pd.read_excel(uploaded_file)
        # Chuẩn hóa tên cột: chuyển về chữ thường và thay khoảng trắng bằng dấu gạch dưới.
        excel_df.columns = [
            col.strip().lower().replace(" ", "_") for col in excel_df.columns
        ]
        # Loại bỏ cột patient_id nếu có
        if "patient_id" in excel_df.columns:
            excel_df = excel_df.drop(columns=["patient_id"])
        st.write("**Nội dung file Excel:**")
        st.dataframe(excel_df, use_container_width=True)

        if st.button("🚀 Thực hiện dự đoán cho file Excel", key="predict_excel"):
            # Lấy số patient_id cao nhất hiện có từ Hive
            cursor.execute("SELECT patient_id FROM cancer_table")
            ids = [row[0] for row in cursor.fetchall()]
            numbers = [
                int(pid[1:]) for pid in ids if pid.startswith("P") and pid[1:].isdigit()
            ]
            start_num = max(numbers) + 1 if numbers else 1
            success_count = 0
            results = []

            for idx, row in excel_df.iterrows():
                try:
                    # Chuẩn bị dữ liệu cho model với các cột expected_features, fill giá trị thiếu bằng 0
                    row_for_pred = pd.DataFrame([row]).reindex(
                        columns=expected_features, fill_value=0
                    )
                    numeric_prediction = model.predict(row_for_pred)[0]
                    # Sử dụng hàm mapping đơn giản
                    prediction_text = map_prediction(numeric_prediction)

                    patient_id = f"P{start_num:03d}"
                    start_num += 1

                    # Chuẩn bị dữ liệu để lưu vào Hive
                    insert_data = {}
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

                    for col in expected_columns:
                        if col == "patient_id":
                            insert_data[col] = patient_id
                        elif col == "level":
                            insert_data[col] = prediction_text
                        elif col in row.index:
                            insert_data[col] = row[col]
                        elif col in row_for_pred.columns:
                            insert_data[col] = row_for_pred[col].iloc[0]
                        else:
                            insert_data[col] = 0

                    # Tạo câu truy vấn INSERT
                    save_df = pd.DataFrame([insert_data], columns=expected_columns)
                    columns_str = ", ".join(save_df.columns)
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

                    cursor.execute(insert_query)
                    conn.commit()
                    success_count += 1
                    results.append({"patient_id": patient_id, "level": prediction_text})
                except Exception as row_err:
                    st.warning(f"Lỗi khi xử lý dòng {idx}: {row_err}")

            if results:
                df_results = pd.DataFrame(results)
                df_results["num"] = df_results["patient_id"].str.lstrip("P").astype(int)
                min_id = f"P{df_results['num'].min():03d}"
                max_id = f"P{df_results['num'].max():03d}"
                st.success(
                    f"Đã xử lý xong file Excel! Lưu thành công {success_count} dòng vào Hive.\nBệnh nhân từ {min_id} đến {max_id}."
                )
                st.write("Bảng kết quả dự đoán:")
                st.dataframe(
                    df_results[["patient_id", "level"]], use_container_width=True
                )
            else:
                st.warning("Không có dòng nào được xử lý.")
    except Exception as e:
        st.error(f"Lỗi xử lý file Excel: {str(e)}")


def fetch_hive_data():
    try:
        cursor.execute("SELECT * FROM cancer_table")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        df.columns = [col.replace("cancer_table.", "") for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Lỗi lấy dữ liệu từ Hive: {e}")
        return pd.DataFrame()


if st.button("🔄 Làm mới dữ liệu", key="refresh", use_container_width=True):
    st.session_state["df_history"] = fetch_hive_data()
    st.rerun()

if "df_history" not in st.session_state:
    st.session_state["df_history"] = fetch_hive_data()

df_history = st.session_state["df_history"]

if not df_history.empty:
    st.write("### Bộ lọc theo từng chỉ số:")
    filtered_df = df_history.copy()

    numeric_cols = [
        c
        for c in filtered_df.columns
        if pd.api.types.is_numeric_dtype(filtered_df[c])
        and c not in ["patient_id", "gender"]
    ]
    categorical_cols = [
        c
        for c in filtered_df.columns
        if (not pd.api.types.is_numeric_dtype(filtered_df[c]) or c == "gender")
        and c != "patient_id"
    ]

    st.write("#### Lọc các cột Numeric")
    chunk_size = 5
    numeric_chunks = [
        numeric_cols[i : i + chunk_size]
        for i in range(0, len(numeric_cols), chunk_size)
    ]
    for chunk in numeric_chunks:
        cols_chunk = st.columns(len(chunk))
        for i, col in enumerate(chunk):
            with cols_chunk[i]:
                st.markdown(f"**{col}**")
                col_data = filtered_df[col].dropna()
                if col_data.empty:
                    lower_val_default = 0
                    upper_val_default = 0
                else:
                    lower_val_default = int(col_data.min())
                    upper_val_default = int(col_data.max())
                lower_val = st.number_input(
                    label="Min",
                    min_value=lower_val_default,
                    max_value=upper_val_default,
                    value=lower_val_default,
                    step=1,
                    key=f"{col}_min",
                )
                upper_val = st.number_input(
                    label="Max",
                    min_value=lower_val_default,
                    max_value=upper_val_default,
                    value=upper_val_default,
                    step=1,
                    key=f"{col}_max",
                )
            filtered_df = filtered_df[
                (filtered_df[col] >= lower_val) & (filtered_df[col] <= upper_val)
            ]

    st.write("#### Lọc các cột Categorical")
    categorical_chunks = [
        categorical_cols[i : i + chunk_size]
        for i in range(0, len(categorical_cols), chunk_size)
    ]
    for chunk in categorical_chunks:
        cols_chunk = st.columns(len(chunk))
        for i, col in enumerate(chunk):
            with cols_chunk[i]:
                st.markdown(f"**{col}**")
                if col == "gender":
                    # Ép giá trị của gender: chỉ hiển thị "Nam" và "Nữ"
                    mapping = {1: "Nam", 2: "Nữ"}
                    unique_numeric = sorted(
                        x for x in filtered_df[col].dropna().unique() if x in mapping
                    )
                    options = [mapping[x] for x in unique_numeric]
                    selected_options = st.multiselect(
                        "Chọn", options, default=options, key=f"{col}_multi"
                    )
                    if selected_options:
                        selected_numeric = [
                            k for k, v in mapping.items() if v in selected_options
                        ]
                        filtered_df = filtered_df[
                            filtered_df[col].isin(selected_numeric)
                        ]
                else:
                    unique_vals = sorted(filtered_df[col].dropna().unique().tolist())
                    if unique_vals:
                        selected_vals = st.multiselect(
                            "Chọn",
                            options=unique_vals,
                            default=unique_vals,
                            key=f"{col}_multi",
                        )
                        if selected_vals:
                            filtered_df = filtered_df[
                                filtered_df[col].isin(selected_vals)
                            ]
    hide_df = filtered_df.drop(columns=["patient_id"])
    st.write("### Kết quả sau khi lọc")
    st.dataframe(hide_df, use_container_width=True)

    # Vẽ biểu đồ thống kê (ví dụ: biểu đồ cột theo level)
    if "level" in filtered_df.columns and not filtered_df["level"].isna().all():
        level_counts = filtered_df["level"].value_counts().reset_index()
        level_counts.columns = ["level", "count"]
        st.write("#### Biểu đồ cột theo Level")
        bar_chart = (
            alt.Chart(level_counts)
            .mark_bar()
            .encode(
                x=alt.X("level:N", sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("count:Q"),
            )
            .properties(width=600, height=400)
        )
        st.altair_chart(bar_chart, use_container_width=True)

    # Vẽ biểu đồ Pie thống kê theo một thuộc tính (ngoại trừ level và patient_id)
    st.write("#### Biểu đồ Pie thống kê theo thuộc tính")

    # Lấy danh sách cột ngoại trừ "level" và "patient_id"
    columns_for_pie = [
        c for c in filtered_df.columns if c not in ["level", "patient_id"]
    ]

    if columns_for_pie:  # Kiểm tra xem còn cột nào hợp lệ không
        selected_col = st.selectbox(
            "Chọn cột để vẽ Pie:", options=columns_for_pie, index=0
        )

        pie_counts = filtered_df[selected_col].value_counts(dropna=False).reset_index()
        pie_counts.columns = [selected_col, "count"]

        pie_chart = (
            alt.Chart(pie_counts)
            .mark_arc()
            .encode(
                theta=alt.Theta("count:Q", stack=True),
                color=alt.Color(
                    f"{selected_col}:N", legend=alt.Legend(title=selected_col)
                ),
                tooltip=[f"{selected_col}:N", "count:Q"],
            )
            .properties(width=400, height=400)
        )

        st.altair_chart(pie_chart, use_container_width=True)
else:
    st.warning("📌 Không có cột nào hợp lệ để vẽ biểu đồ Pie!")
