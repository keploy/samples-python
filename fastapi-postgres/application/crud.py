from sqlalchemy.orm import Session
from . import models, schemas


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_byEmail(db: Session, student_email: str):
    return db.query(models.Student).filter(models.Student.email == student_email).first()


def get_students(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: schemas.StudentCreate):
    student_hashed_password = password_hasher(student.password)

    db_student = models.Student(name=student.name, email=student.email, password=student_hashed_password)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student: schemas.StudentUpdate, student_id: int):
    student_old = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student_old is None:
        return None
    student_old.name = student_old.name if student.name is None else student.name
    student_old.email = student_old.email if student.email is None else student.email
    student_old.stream = student_old.stream if student.stream is None else student.stream
    student_old.password = password_hasher(student.password)
    db.commit()
    db.refresh(student_old)
    return student_old


def delete_student(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return student


def password_hasher(password) -> str:
    hashed_password = 's'
    for i in range(0, len(password)):
        hashed_password += chr(ord(password[i]) + 1)
    return hashed_password
