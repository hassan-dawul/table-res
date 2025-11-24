from sqlalchemy import Column, Integer, String, DateTime, Time, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from db import Base  # تأكد أن Base مستورد من db
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime



# -------------------------------
# جدول المستخدمين
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    token = Column(String(100), nullable=True)  # لتخزين توكن الجلسة أو أي مفتاح
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    role = Column(String(50), default="user", nullable=False)

    # علاقة الحجوزات: كل مستخدم يمكن أن يكون له عدة حجوزات
    bookings = relationship("Booking", back_populates="user")

# -------------------------------
# جدول المطاعم
class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)       # جديد
    area = Column(String(100), nullable=False)
    area_en = Column(String(100), nullable=True)       # جديد
    cuisine = Column(String(100), nullable=False)
    cuisine_en = Column(String(100), nullable=True)    # جديد
    opens_at = Column(Time, nullable=False)
    closes_at = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # علاقة الحجوزات: كل مطعم يمكن أن يكون له عدة حجوزات
    bookings = relationship("Booking", back_populates="restaurant")

# -------------------------------
# تعريف Enum لحالة الحجز
class BookingStatus(PyEnum):
    pending = "pending" 
    confirmed = "confirmed"
    cancelled = "cancelled"

# -------------------------------
# جدول الحجوزات
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)  # يمكنك استخدام Date فقط إذا أحببت
    time = Column(Time, nullable=False)
    people = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.pending)  # تعديل هنا
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # الربط بالعلاقات
    user = relationship("User", back_populates="bookings")
    restaurant = relationship("Restaurant", back_populates="bookings")

 # إعداد نموذج الرسائل في قاعدة 

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
