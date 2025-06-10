import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import joblib
from telegram import Message


class TypeConverter(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.columns:
            if col in X.columns:
                X[col] = X[col].astype(str)
        return X


async def train_model(message: Message):
    csv_path = os.path.join("data", "data.csv")
    model_path = os.path.join("model", "model.pkl")

    if not os.path.exists(csv_path):
        await message.reply_text(
            "❌ CSV файл не найден. Пожалуйста, сначала загрузите данные."
        )
        return

    if os.path.exists(model_path):
        await message.reply_text(
            "⚠️ Модель уже существует.\n" "🔄 Переобучаю модель на новых данных..."
        )
    else:
        await message.reply_text("🤖 Начинаю обучение новой модели...")

    try:
        df = pd.read_csv(csv_path)

        current_year = pd.Timestamp.now().year

        required_columns = ["Общая площадь", "Цена"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            await message.reply_text(
                f"❌ Отсутствуют необходимые колонки: {', '.join(missing_columns)}"
            )
            return

        filters = []
        if "Общая площадь" in df.columns:
            filters.append(df["Общая площадь"] <= 200)
        if "Этаж" in df.columns:
            filters.append(df["Этаж"] <= 50)
        if "Год постройки" in df.columns:
            filters.append(df["Год постройки"] >= (current_year - 100))
        if "Высота потолков" in df.columns:
            filters.append(df["Высота потолков"] <= 5)
        if "Цена" in df.columns:
            filters.append(df["Цена"] <= 100000000)
        if "Площадь кухни" in df.columns:
            filters.append(df["Площадь кухни"] <= 50)

        if filters:
            df_cleaned = df[np.all(filters, axis=0)]
        else:
            df_cleaned = df

        if len(df_cleaned) < 10:
            await message.reply_text(
                "❌ После фильтрации осталось слишком мало данных для обучения."
            )
            return

        X = df_cleaned.drop(columns=["Цена"])
        y = df_cleaned["Цена"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        categorical_features = X_train.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    OneHotEncoder(
                        drop="first", handle_unknown="ignore", sparse_output=False
                    ),
                    categorical_features,
                )
            ],
            remainder="passthrough",
        )

        pipeline = Pipeline(
            [
                ("type_converter", TypeConverter(columns=categorical_features)),
                ("preprocessor", preprocessor),
                (
                    "model",
                    RandomForestRegressor(random_state=42, n_estimators=100, n_jobs=-1),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        if not os.path.exists("model"):
            os.makedirs("model")

        model_path = os.path.join("model", "model.pkl")
        joblib.dump(pipeline, model_path)

        report = f"""✅ **Модель успешно обучена!**
            📊 **Результаты обучения:**
            • R² Score: {r2:.4f}
            • RMSE: {rmse:,.2f} руб.
            • MAPE: {mape:.2f}%

            📈 **Информация о данных:**
            • Всего объектов: {len(df_cleaned):,}
            • Обучающая выборка: {len(X_train):,}
            • Тестовая выборка: {len(X_test):,}
            • Количество признаков: {X.shape[1]}

            ✅ Модель сохранена и готова к использованию!"""

        await message.reply_text(report, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Ошибка при обучении модели: {str(e)}")
