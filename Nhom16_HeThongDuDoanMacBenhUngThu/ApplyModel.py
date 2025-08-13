import pandas as pd


def rm_main(model, data: pd.DataFrame):
    base = data.drop(columns=["level", "age", "gender"])
    data["predicted"] = model.predict(base)
    data.rm_metadata["predicted"] = (None, "prediction")

    return data
