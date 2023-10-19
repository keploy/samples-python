from sqlalchemy import Integer, String, Column

from .database import Base


class Student(Base):
    __tablename__="students"

    id = Column(Integer, name="ID", primary_key=True, index=True, info="Stores the id of a student", autoincrement="auto")
    name = Column(String, name="Name")
    email = Column(String, name="Email", index=True)
    password = Column(String, name="Hashed Password")
    stream = Column(String, name="Subject Stream", default="Mathematics")
