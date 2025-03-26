import pickle
import subprocess
import webbrowser


def rm_main(model):
    """
    Hàm chính của RapidMiner nhận:
    - model: Mô hình đã huấn luyện
    - data: DataFrame chưa có label
    """
    # Chạy Streamlit trong một luồng riêng
    with open("model/model.pkl", "wb") as f:
        pickle.dump(model, f)

    subprocess.Popen(["streamlit", "run", "Cancer Prediction.py"], shell=True)

    webbrowser.open("http://localhost:8501")
    return "Streamlit UI đã được mở!"
