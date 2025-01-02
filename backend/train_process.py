import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.compose import ColumnTransformer
from category_encoders import LeaveOneOutEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Dict


class RoomTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, column="Кол-во комнат"):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_ = X.copy()
        X_[self.column] = X_[self.column].apply(self.transform_rooms)
        return X_

    def transform_rooms(self, value):
        if value == "5+":
            return 5
        elif value == "free":
            return 0.5
        else:
            return int(value)


def build_pipeline(alpha=1.0, max_iter=1000):
    categorical_features = ["Ремонт", "Материал стен", "Тип жилья"]
    preprocessor = ColumnTransformer(
        transformers=[
            ("room_transform", RoomTransformer("Кол-во комнат"), ["Кол-во комнат"]),
            ("loo_encoder", LeaveOneOutEncoder(sigma=0.4), ["Станция"]),
            ("cat", OneHotEncoder(drop="first", sparse_output=False), categorical_features),
        ],
        remainder="passthrough",
    )

    pipeline = Pipeline(
        [("preprocessor", preprocessor), ("scaler", StandardScaler()), ("model", Ridge(alpha=alpha, max_iter=max_iter))]
    )
    return pipeline


def train_pipeline(df: List[Dict], pipeline, test_size=0.3, random_state=42):
    # if not os.path.exists(csv_path):
    #     raise FileNotFoundError("CSV dataset not found! Please upload it first.")

    # df = pd.read_csv(csv_path, sep=',', engine='python')
    df = pd.DataFrame(df)
    if "Цена" not in df.columns:
        raise ValueError("Колонка 'Цена' не найдена в CSV! " "Проверьте, что в вашем CSV столбец назван именно 'Цена'.")

    X = df.drop("Цена", axis=1)
    y = df["Цена"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)

    return pipeline, r2, rmse
