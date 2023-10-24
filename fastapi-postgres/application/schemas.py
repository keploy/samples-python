from pydantic import BaseModel


class StudentBase(BaseModel):
    name: str
    email: str


class StudentCreate(StudentBase):
    password: str


class StudentUpdate(StudentCreate):
    stream: str

    class Config:
        from_attributes = True


class Student(StudentUpdate):
    id: int

    class Config:
        from_attributes = True
