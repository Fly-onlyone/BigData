import pandas as pd
from sklearn.tree import DecisionTreeClassifier


def rm_main(data: pd.DataFrame):
    model = DecisionTreeClassifier()
    base = data.drop(columns=["level", "age", "gender"])

    model.fit(base, data["level"])

    return model
