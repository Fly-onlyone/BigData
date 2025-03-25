import pickle
import subprocess
import threading
import webbrowser


def run_streamlit(model):
    """Chạy Streamlit với mô hình và dữ liệu dự đoán."""
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    subprocess.Popen(["streamlit", "run", "Cancer Prediction.py"], shell=True)


def rm_main(model):
    """
    Hàm chính của RapidMiner nhận:
    - model: Mô hình đã huấn luyện
    - data: DataFrame chưa có label
    """
    # Chạy Streamlit trong một luồng riêng
    run_streamlit(model)
    webbrowser.open("http://localhost:8501")
    return "Streamlit UI đã được mở!"
