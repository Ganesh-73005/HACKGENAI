from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")

class Scene(BaseModel):
    description: str
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    replicate_id: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    camera_angle: Optional[str] = None
    lens: Optional[str] = None
    lighting: Optional[str] = None
    scene_number: Optional[int] = None
    duration: Optional[float] = None
    notes: Optional[str] = None

class Story(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    theme: str
    genre: Optional[str] = None
    scenes: List[Scene] = []
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "draft"  # draft, processing, completed
    total_scenes: Optional[int] = None
    estimated_duration: Optional[float] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    subscription_tier: str = "free"  # free, pro, enterprise

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class GenerateImageRequest(BaseModel):
    story_id: str
    scene_index: int
    prompt: Optional[str] = None
    style: Optional[str] = "cinematic"
    aspect_ratio: Optional[str] = "16:9"
    reference_images: Optional[List[str]] = None

class GenerateVideoRequest(BaseModel):
    story_id: str
    scene_indices: List[int]
    duration: Optional[int] = 5
    fps: Optional[int] = 24
    resolution: Optional[str] = "1080p"

class UpdateSceneRequest(BaseModel):
    description: Optional[str] = None
    camera_angle: Optional[str] = None
    lens: Optional[str] = None
    lighting: Optional[str] = None
    notes: Optional[str] = None

class StoryCreateRequest(BaseModel):
    title: str
    theme: str
    genre: Optional[str] = None
    prompt: Optional[str] = None
