import pandas as pd


def rm_main(model, data: pd.DataFrame):
    base = data.drop(columns=['Level'])
    data['Predicted'] = model.predict(base)
    data.rm_metadata['Predicted'] = (None, 'prediction')
    return data