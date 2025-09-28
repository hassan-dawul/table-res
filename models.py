from sqlalchemy import Column, Integer, String, DateTime, Time, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from db import Base  # تأكد إن Base مستورد من db

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    token = Column(String(100), nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    bookings = relationship("Booking", back_populates="user")

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    cuisine = Column(String(100), nullable=False)
    opens_at = Column(Time, nullable=False)
    closes_at = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    bookings = relationship("Booking", back_populates="restaurant")

# تعريف enum لحالة الحجز
class BookingStatus(PyEnum):
    confirmed = "confirmed"
    cancelled = "cancelled"

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)  # ممكن تستخدم Date فقط لو تحب
    time = Column(Time, nullable=False)
    people = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.confirmed)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="bookings")
    restaurant = relationship("Restaurant", back_populates="bookings")
