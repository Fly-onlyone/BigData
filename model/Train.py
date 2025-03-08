def train_with_model(data, model):
    base = data.drop(columns=['Level'])
    model.fit(base, data['Level'])
    return model
