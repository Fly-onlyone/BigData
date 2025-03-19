import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from Train import train_with_model


def rm_main(data: pd.DataFrame):
    model = RandomForestClassifier()
    return train_with_model(data, model)
