from sklearn.preprocessing import LabelEncoder

def train_with_model(data, model):
    base = data.drop(columns=['level'])

    for col in base.columns:
        if base[col].dtype == 'object':
            le = LabelEncoder()
            base[col] = le.fit_transform(base[col])

    model.fit(base, data['level'])
    return model
