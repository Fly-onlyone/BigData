def rm_main(model, data):
    base = data.drop(columns=['Level'])
    data['Predicted'] = model.predict(base)
    data.rm_metadata['Predicted'] = (None, 'prediction')
    return data, data.rm_metadata
