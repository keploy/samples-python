from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI(title="Student Management API (FastAPI + MongoDB)")

# MongoDB connection
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.students_db
collection = db.students

class Student(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    name: str
    age: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

@app.post("/students", response_model=Student)
async def create_student(student: Student):
    student_dict = student.dict(by_alias=True)
    student_dict.pop("id", None)
    result = await collection.insert_one(student_dict)
    student_dict["_id"] = str(result.inserted_id)
    return Student(**student_dict)

@app.get("/students", response_model=List[Student])
async def get_students():
    students = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        students.append(Student(**doc))
    return students

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    student = await collection.find_one({"_id": ObjectId(student_id)})
    if student:
        student["_id"] = str(student["_id"])
        return Student(**student)
    raise HTTPException(status_code=404, detail="Student not found")

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student: Student):
    student_dict = student.dict(by_alias=True)
    student_dict.pop("id", None)
    result = await collection.update_one(
        {"_id": ObjectId(student_id)}, {"$set": student_dict}
    )
    if result.modified_count == 1:
        updated = await collection.find_one({"_id": ObjectId(student_id)})
        updated["_id"] = str(updated["_id"])
        return Student(**updated)
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 1:
        return {"message": "Student deleted"}
    raise HTTPException(status_code=404, detail="Student not found")
