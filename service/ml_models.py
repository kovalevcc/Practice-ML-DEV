import pickle

def load_model(model_name: str):
    with open(f'models/{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def predict(model_name: str, input_data: str):
    model = load_model(model_name)
    prediction = model.predict([input_data])
    return prediction[0]