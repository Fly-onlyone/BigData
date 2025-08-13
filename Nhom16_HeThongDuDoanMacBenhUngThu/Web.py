import os
import pickle
import subprocess
import time

import pandas as pd
import psutil

PORT_FILE = "port/streamlit_port.txt"
DEFAULT_PORT = 8501
BROWSER_LOCK_FILE = "port/browser_opened.lock"


def find_running_streamlit():
    for proc in psutil.process_iter(attrs=["pid", "cmdline"]):
        try:
            cmd = proc.info["cmdline"]
            if cmd and "streamlit" in cmd and "run" in cmd:
                for arg in cmd:
                    if "--server.port=" in arg:
                        return proc, int(arg.split("=")[1])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None, None


def save_predictions_to_excel(
    predicted_trainset, predicted_testset, filename="data/predictions.xlsx"
):
    os.makedirs("data", exist_ok=True)

    combined_df = pd.concat([predicted_trainset, predicted_testset], ignore_index=True)

    with pd.ExcelWriter(filename, engine="xlsxwriter", mode="w") as writer:
        combined_df.to_excel(writer, sheet_name="Predictions", index=False)


def rm_main(model, predicted_trainset, predicted_testset):
    os.makedirs("model", exist_ok=True)

    with open("model/model.pkl", "wb") as f:
        pickle.dump(model, f)
    save_predictions_to_excel(predicted_trainset, predicted_testset)
    old_proc, old_port = find_running_streamlit()

    if old_proc:
        print(f"Stopping existing Streamlit process (PID: {old_proc.pid})...")
        old_proc.terminate()
        old_proc.wait()
        time.sleep(2)

    port = old_port or DEFAULT_PORT

    os.makedirs(os.path.dirname(PORT_FILE), exist_ok=True)
    with open(PORT_FILE, "w") as f:
        f.write(str(port))

    subprocess.Popen(
        ["streamlit", "run", "Cancer Prediction.py", "--server.port", str(port)],
        shell=True,
    )

    return None
