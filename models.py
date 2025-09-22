from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# تعريف قاعدة الـ ORM
Base = declarative_base()

# جدول المستخدمين
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    token = Column(String(100), nullable=True)


# جدول المطاعم
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    cuisine = Column(String(100), nullable=False)
