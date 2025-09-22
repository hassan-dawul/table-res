from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db import Base  # تأكد إن Base مستورد من db

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    token = Column(String(100))
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# ✨ إضافة فئة Restaurant
class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    cuisine = Column(String(100), nullable=False)
