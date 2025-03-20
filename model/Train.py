def train_with_model(data, model):
    base = data.drop(columns=['level'])
    model.fit(base, data['level'])
    return model
