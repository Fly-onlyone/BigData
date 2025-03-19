import pandas as pd
from sklearn.naive_bayes import GaussianNB

from Train import train_with_model


def rm_main(data: pd.DataFrame):
    model = GaussianNB()
    return train_with_model(data, model)
