"""Bước cuối của process RapidMiner (operator Execute Python).

Lưu model và kết quả dự đoán, rồi khởi động (hoặc khởi động lại) ứng dụng Streamlit.
"""

import os
import pickle
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import psutil

BASE_DIR = Path(__file__).resolve().parent
PORT_FILE = BASE_DIR / "port" / "streamlit_port.txt"
DEFAULT_PORT = 8501


def find_running_streamlit():
    for proc in psutil.process_iter(attrs=["pid", "cmdline"]):
        try:
            cmd = proc.info["cmdline"]
            if cmd and "streamlit" in cmd and "run" in cmd:
                for arg in cmd:
                    if arg.startswith("--server.port="):
                        return proc, int(arg.split("=")[1])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None, None


def save_predictions_to_excel(
    predicted_trainset,
    predicted_testset,
    filename=BASE_DIR / "data" / "predictions.xlsx",
):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    combined_df = pd.concat([predicted_trainset, predicted_testset], ignore_index=True)

    with pd.ExcelWriter(filename, engine="xlsxwriter", mode="w") as writer:
        combined_df.to_excel(writer, sheet_name="Predictions", index=False)


def rm_main(model, predicted_trainset, predicted_testset):
    os.makedirs(BASE_DIR / "model", exist_ok=True)

    with open(BASE_DIR / "model" / "model.pkl", "wb") as f:
        pickle.dump(model, f)
    save_predictions_to_excel(predicted_trainset, predicted_testset)
    old_proc, old_port = find_running_streamlit()

    if old_proc:
        print(f"Stopping existing Streamlit process (PID: {old_proc.pid})...")
        old_proc.terminate()
        old_proc.wait()
        time.sleep(2)

    port = old_port or DEFAULT_PORT

    os.makedirs(PORT_FILE.parent, exist_ok=True)
    PORT_FILE.write_text(str(port))

    # Truyền danh sách tham số, không qua shell. "--server.port=<port>" viết liền
    # để find_running_streamlit() đọc lại được cổng ở lần chạy sau.
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", f"--server.port={port}"],
        cwd=BASE_DIR,
    )

    return None
