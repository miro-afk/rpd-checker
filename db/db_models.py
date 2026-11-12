from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Headers(Base):
    __tablename__ = "headers"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

class Competentions(Base):
    __tablename__ = "competentions"
    id = Column(Integer, primary_key=True, index=True)
    content =Column(Text, nullable=False)
    speciality = Column(Text, nullable=False)
