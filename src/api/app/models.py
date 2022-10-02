"""Defines pydantic models"""
from typing import Optional, Any

from pydantic import BaseModel


class FilterProductsModel(BaseModel):
    gender: Optional[str]
    master_category: Optional[str]
    sub_category: Optional[str]
    article_type: Optional[str]
    base_colour: Optional[str]
    season: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    limit: Optional[int]
    usage: Optional[str]
    augmentation_config: Optional[dict] = None


class TaskResult(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    result: Optional[Any] = None


class InferenceModel(BaseModel):
    s3_target: str
