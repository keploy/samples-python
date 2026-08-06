# app/routes/parent.py
import bcrypt
from fastapi import APIRouter, HTTPException
from quizzly.models.parent import Parent, ParentCreate
from quizzly.db.mongodb import db
from quizzly.utils.jwt import create_token
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter()


@router.post("/register")
async def register_parent(data: ParentCreate):
    parent_data = Parent(**data.dict())
    parent_data.password = bcrypt.hashpw(parent_data.password.encode(), bcrypt.gensalt()).decode()
    await db.parents.insert_one(parent_data.model_dump(by_alias=True))
    parent = await db.parents.find_one({"username": parent_data.username})
    token = create_token({"id": str(parent["_id"])})
    return {"message": "Parent registered successfully", "access_token": token}


@router.post("/login")
async def login(data: LoginRequest):
    parent = await db.parents.find_one({"username": data.username})
    if not parent:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt.checkpw(data.password.encode(), parent["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_token({"id": str(parent["_id"])})
    return {"access_token": token}
