# app/models/parent.py
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class ParentCreate(BaseModel):
    username: str
    password: str
    name: Optional[str]


class Parent(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    username: str
    password: str
