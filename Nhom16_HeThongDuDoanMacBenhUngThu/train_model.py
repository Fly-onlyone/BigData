"""Huấn luyện lại Decision Tree từ Cancer.csv mà không cần RapidMiner.

Model lưu ra trả thẳng nhãn "Low"/"Medium"/"High", nên app.py không phải đoán thứ tự
mã hóa số như với model xuất từ RapidMiner.

    python train_model.py
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "docker" / "shared-data" / "Cancer.csv"
MODEL_PATH = BASE_DIR / "model" / "model.pkl"

# Giống process RapidMiner: bỏ patient_id, age, gender; dự đoán level.
FEATURES = [
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
TARGET = "level"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def main() -> None:
    df = load_data()
    model = DecisionTreeClassifier(random_state=42)
    model.fit(df[FEATURES], df[TARGET])

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(
        f"Đã lưu {MODEL_PATH.relative_to(BASE_DIR)}: {len(df)} dòng, "
        f"độ sâu {model.get_depth()}, {model.get_n_leaves()} lá, nhãn {list(model.classes_)}"
    )


if __name__ == "__main__":
    main()
