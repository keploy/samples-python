from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import asyncio

from . import models, crud, schemas

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/studentdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/students/', response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student_byEmail(db, student_email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Student already registered!!")
    data = crud.create_student(db, student=student)
    return data

@app.get('/students/', response_model=list[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip, limit)
    if students == []:
        raise HTTPException(404, 'Data not found!!')
    return students

@app.get('/students/{student_id}', response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f'Student with ID={student_id} not found!!')
    return student

@app.put('/students/{student_id}', response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student=student, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f'Student with ID={student_id} not found!!')
    return student

@app.delete('/students/{student_id}', response_model=schemas.Student)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.delete_student(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f'Student with ID={student_id} not found!!')
    return student

# Graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Example: Close the database connection pool
    print("Shutting down...")
    # Assuming SQLAlchemy engine has a dispose method to release resources
    engine.dispose()

