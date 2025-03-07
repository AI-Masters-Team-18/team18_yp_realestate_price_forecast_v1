from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    model_id: str = Field(..., description="Уникальный ID модели")
    description: str = Field(..., description="Описание модели")
    is_active: bool = Field(..., description="Флаг активности")
    detailed_info: Optional[Dict[str, float]] = Field(None, description="модели")


class ModelListResponse(BaseModel):
    models: List[ModelInfo]


class SetModelRequest(BaseModel):
    model_id: str


class FitRequest(BaseModel):
    model_id: str
    hyperparams: Dict[str, float]
    dataframe: List[Dict]


class LearningCurveResponse(BaseModel):
    response: Dict[str, List[float]] = Field(..., description="Словарь, содержащий метрики кривой обучения")


class FitResponse(BaseModel):
    status: str
    message: str


class PredictRequest(BaseModel):
    model_id: Optional[str] = Field(None, description="ID модели")
    input_data: Dict[str, str]


class PredictResponse(BaseModel):
    prediction: float


class CreateModelRequest(BaseModel):
    model_id: str


class CreateModelResponse(BaseModel):
    status: str
    message: str


class UploadDatasetResponse(BaseModel):
    message: str


class EDAResponse(BaseModel):
    eda_info: dict
