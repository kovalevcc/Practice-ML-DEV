import pickle
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import json


def process_data(filename, model_name):
    data = pd.read_csv(filename)
    data.columns = [
        "product_id",
        "product_title",
        "merchant_id",
        "cluster_id",
        "cluster_label",
        "category_id",
        "category_label",
    ]

    with open('models/category_mapping.json', 'r') as json_file:
        category_mapping = json.load(json_file)

    category_mapping = {int(k): v for k, v in category_mapping.items()}

    tfidf = pickle.load(open("models/tfidf.pkl", "rb"))
    x = tfidf.transform(data["product_title"])

    model = pickle.load(open(f"models/{model_name}.pkl", "rb"))
    data['predicted_category_id'] = model.predict(x)
    data['category_label'] = data['predicted_category_id'].map(
        category_mapping)

    output_filename = f"{filename.split('.')[0]}_processed.csv"
    data.to_csv(output_filename, index=False, sep=';')

    return output_filename
