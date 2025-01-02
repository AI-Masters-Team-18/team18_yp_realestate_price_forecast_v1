import logging
import os
from re import S
from urllib import response
from matplotlib.pylab import det
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from typing import Annotated

import pip
from streamlit import dataframe

from models import (
    ModelListResponse, ModelInfo, SetModelRequest,
    FitRequest, FitResponse, PredictRequest, PredictResponse,
    CreateModelRequest, CreateModelResponse,
    UploadDatasetResponse, EDAResponse, LearningCurveResponse
)
from logging_config import setup_logging
from train_process import build_pipeline, train_pipeline

app = FastAPI()
logger = setup_logging()

MODELS = {
}

@app.on_event("startup")
def startup_event():
    logger.info("Приложение запущено. MODELS dict инициализирован пустым/базовым.")

@app.get("/models", response_model=ModelListResponse)
def get_models():
    model_list = []
    for mid, data in MODELS.items():
        model_list.append(ModelInfo(
            model_id=mid,
            description=data["description"],
            is_active=data["is_active"],
            detailed_info=data.get("detailed_info")
            ))
    return ModelListResponse(models=model_list)

@app.post("/models/create", response_model=CreateModelResponse)
def create_model(req: CreateModelRequest):
    if req.model_id in MODELS:
        raise HTTPException(status_code=400, detail="Model already exists")

    MODELS[req.model_id] = {
        "description": "Custom Ridge model, hyperparams set at fit time",
        "is_active": False,
        "pipeline": None
    }
    logger.info(f"Создана модель {req.model_id}")
    return CreateModelResponse(status="OK", message=f"Model {req.model_id} created")

@app.post("/models/set", response_model=FitResponse)
def set_active_model(req: SetModelRequest):
    mid = req.model_id
    if mid not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    for m in MODELS:
        MODELS[m]["is_active"] = False
    MODELS[mid]["is_active"] = True

    logger.info(f"Установлена активная модель: {mid}")
    return FitResponse(status="OK", message=f"Active model set to {mid}")

@app.post("/fit", response_model=FitResponse)
def fit_model(req: FitRequest, background_tasks: BackgroundTasks):
    mid = req.model_id
    if mid not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")
    def do_fit():
        try:
            alpha = float(req.hyperparams.get("alpha", 1.0))
            max_iter = int(req.hyperparams.get("max_iter", 1000))
            if alpha <= 0 or max_iter <= 0:
                raise HTTPException(status_code=400, detail="Invalid hyperparameters")
            pipeline = build_pipeline(alpha=alpha, max_iter=max_iter)
            dataframe = req.dataframe
            trained_pipeline, r2, rmse = train_pipeline(dataframe, pipeline)
            MODELS[mid]["pipeline"] = trained_pipeline
            logger.info(f"Модель {mid} обучена: R2={r2:.4f}, RMSE={rmse:.4f}")
            
        except Exception as e:
            logger.error(f"Ошибка при обучении модели {mid}: {e}")

    background_tasks.add_task(do_fit)
    logger.info(f"Запущено обучение для модели {mid} (фон).")

    return FitResponse(status="RUNNING", message=f"Training model {mid} started.")

@app.get("/models/{mid}", response_model=ModelInfo)
def get_model_info(mid: str):
    if mid not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")
    
    pipeline = MODELS[mid]["pipeline"]
    description = MODELS[mid]["description"]
    is_active = MODELS[mid]["is_active"] 
    
    if pipeline is None:
        return ModelInfo(
            model_id=mid,
            description=MODELS[mid]["description"],
            is_active=MODELS[mid]["is_active"],
            detailed_info=None
        )
        
    model = pipeline.named_steps['model']
    alpha = model.alpha
    max_iter = model.max_iter
    coefficients = model.coef_
    intercept = model.intercept_
    feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
    coefficients_dict = {feature: coef for feature, coef in zip(feature_names, coefficients)}
    detailed_info = {
        "alpha": alpha,
        "max_iter": max_iter,
        "coefficients_dict": coefficients_dict,
        "intercept": intercept,
    }
    MODELS[mid]["detailed_info"] = detailed_info
    response = ModelInfo(
        model_id=mid,
        description=description,
        is_active=is_active,
        detailed_info=detailed_info if detailed_info else None
    )
    return response
    

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    mid = req.model_id
    if not mid:
        active = None
        for k, v in MODELS.items():
            if v["is_active"]:
                active = k
                break
        if not active:
            raise HTTPException(status_code=404, detail="No active model found")
        mid = active

    if mid not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    pipeline = MODELS[mid]["pipeline"]
    if pipeline is None:
        raise HTTPException(status_code=400, detail="Model is not trained yet")

    df_input = pd.DataFrame([req.input_data])
    y_pred = pipeline.predict(df_input)[0]
    logger.info(f"Predict model={mid}, input={req.input_data}, y={y_pred}")
    return PredictResponse(prediction=y_pred)

@app.post("/upload-dataset", response_model=UploadDatasetResponse)
def upload_dataset(file: Annotated[UploadFile, File(...)]):
    """
    Загрузка CSV в /app/data/df_filtered.csv
    """
    file_name = file.filename
    if file_name and not file_name.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    os.makedirs("/app/data", exist_ok=True)
    save_path = "/app/data/df_filtered.csv"

    content = file.file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    file.file.close()

    logger.info(f"Загружен файл {file.filename}, сохранён как {save_path}, байт={len(content)}")
    return UploadDatasetResponse(message=f"Uploaded {file.filename} => df_filtered.csv")

@app.get("/eda", response_model=EDAResponse)
def get_eda():
    """
    Пример EDA: читаем df_filtered.csv, возвращаем describe()
    """
    csv_path = "/app/data/df_filtered.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV not found. Please upload first.")

    try:
        df = pd.read_csv(csv_path, sep=',', engine='python')
        if 'Цена' not in df.columns:
            raise HTTPException(status_code=500, detail="Колонка 'Цена' не найдена в CSV.")

        try:
            desc = df.describe().to_dict()
        except:
            desc = {}

        info = {
            "rows": df.shape[0],
            "cols": df.shape[1],
            "columns": list(df.columns),
            "describe": desc
        }
        return EDAResponse(eda_info=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

from sklearn.model_selection import learning_curve
@app.post("/learning-curve", response_model=LearningCurveResponse)
def get_learning_curve(req: FitRequest):
    model_id = req.model_id
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")
    #на данном этапе модель всегда должна быть обучена, гиперпараметры передаются прямо в ней
    model = MODELS[model_id]["pipeline"].named_steps['model']
    df = pd.DataFrame(req.dataframe)
    
    X = df.drop('Цена', axis=1)
    y = df['Цена']
    
    # Вычисление learning curve
    train_sizes = [0.1, 0.25, 0.5, 0.75, 1.0]
    try: 
        train_sizes_abs, train_scores, test_scores, _, _ = learning_curve(model, X, y, train_sizes=train_sizes, cv=5, scoring="neg_mean_squared_error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during learning curve calculation: {str(e)}")
    
    response_structure  = {
        "train_sizes": train_sizes_abs.tolist(),
        "train_scores": (-train_scores.mean(axis=1)).tolist(),
        "test_scores": (-test_scores.mean(axis=1)).tolist()
    }
    # Возвращение результатов
    return LearningCurveResponse(response=response_structure)