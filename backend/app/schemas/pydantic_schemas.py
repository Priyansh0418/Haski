from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class ProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    allergies: Optional[str] = None
    lifestyle: Optional[str] = None
    skin_type: Optional[str] = None
    hair_type: Optional[str] = None


class ProfileRead(ProfileCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


class PhotoCreate(BaseModel):
    filename: Optional[str] = None
    s3_key: Optional[str] = None


class PhotoRead(PhotoCreate):
    id: int
    user_id: int
    uploaded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    photo_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    skin_type: Optional[str] = None
    hair_type: Optional[str] = None
    # conditions can be a list or dict depending on the model output
    conditions: Optional[Any] = None
    # confidence_scores usually a mapping from label->score
    confidence_scores: Optional[Dict[str, float]] = None

    model_config = {"from_attributes": True}
from pydantic import BaseModel
from typing import Optional, List


class Profile(BaseModel):
    username: str
    age: Optional[int]
    gender: Optional[str]
    skin_type: Optional[str]
    hair_type: Optional[str]


class AnalysisResult(BaseModel):
    skin_type: Optional[str]
    hair_type: Optional[str]
    conditions: List[str]
    confidence: float


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class AnalysisResponse(BaseModel):
    skin_type: str
    hair_type: str
    conditions_detected: List[str]
    confidence_scores: dict


### DB models schemas


class UserCreate(BaseModel):
    username: str
    email: Optional[str]
    password: Optional[str]


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]

    model_config = {"from_attributes": True}


class ProfileIn(BaseModel):
    age: Optional[int]
    gender: Optional[str]
    location: Optional[str]
    allergies: Optional[str]
    lifestyle: Optional[str]


class ProfileOut(ProfileIn):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


class PhotoOut(BaseModel):
    id: int
    filename: str
    s3_key: Optional[str]
    uploaded_at: Optional[str]

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    id: int
    user_id: int
    photo_id: Optional[int]
    timestamp: Optional[str]
    skin_type: Optional[str]
    hair_type: Optional[str]
    conditions: Optional[str]
    confidence_scores: Optional[dict]

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    id: int
    user_id: int
    created_at: Optional[str]
    content: str
    source: Optional[str]

    model_config = {"from_attributes": True}


class FeedbackOut(BaseModel):
    id: int
    user_id: int
    analysis_id: Optional[int]
    rating: Optional[int]
    comment: Optional[str]
    created_at: Optional[str]

    model_config = {"from_attributes": True}
