import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .database import Base, SessionLocal
from . import crud, models, schemas

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_create_student(db_session):
    student_in = schemas.StudentCreate(name="John Doe", email="john.doe@example.com", password="password", stream="Science")
    student = crud.create_student(db_session, student_in)
    assert student.name == "John Doe"
    assert student.email == "john.doe@example.com"

def test_get_student(db_session):
    student_in = schemas.StudentCreate(name="Jane Doe", email="jane.doe@example.com", password="password", stream="Arts")
    student = crud.create_student(db_session, student_in)
    fetched_student = crud.get_student(db_session, student.id)
    assert fetched_student.name == "Jane Doe"
    assert fetched_student.email == "jane.doe@example.com"

def test_update_student(db_session):
    student_in = schemas.StudentCreate(name="Jim Beam", email="jim.beam@example.com", password="password", stream="Commerce")
    student = crud.create_student(db_session, student_in)
    student_update = schemas.StudentUpdate(name="Jim Updated", email="jim.updated@example.com", password="newpassword", stream="Commerce")
    updated_student = crud.update_student(db_session, student_update, student.id)
    assert updated_student.name == "Jim Updated"
    assert updated_student.email == "jim.updated@example.com"

def test_delete_student(db_session):
    student_in = schemas.StudentCreate(name="Will Smith", email="will.smith@example.com", password="password", stream="Engineering")
    student = crud.create_student(db_session, student_in)
    deleted_student = crud.delete_student(db_session, student.id)
    assert deleted_student is not None
    assert deleted_student.name == "Will Smith"
    assert crud.get_student(db_session, student.id) is None
