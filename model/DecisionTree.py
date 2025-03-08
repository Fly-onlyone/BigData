import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from Train import train_with_model


def rm_main(data: pd.DataFrame):
    model = DecisionTreeClassifier()
    return train_with_model(data, model)
