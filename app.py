from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends, Body
from fastapi.responses import JSONResponse
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
import secrets

from pydantic import BaseModel, validator, EmailStr
from db import SessionLocal, engine, Base
from models import User, Restaurant
from enum import Enum
from pydantic import conint
from datetime import date as date_type, time as time_type
from fastapi import HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from models import User


# استيراد موديل الحجز و enum الخاص بالحالة
from models import Booking, BookingStatus


app = FastAPI()

# إنشاء الجداول عند بدء التشغيل
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class RestaurantCreate(BaseModel):
    name: str
    area: str
    cuisine: str
    opens_at: str
    closes_at: str
    capacity: int

    @validator('opens_at', 'closes_at')
    def check_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM.")
        return v

    @validator('capacity')
    def capacity_positive(cls, v):
        if v <= 0:
            raise ValueError("السعة يجب أن تكون أكبر من صفر.")
        return v

class RestaurantUpdate(BaseModel):
    name: Optional[str]
    area: Optional[str]
    cuisine: Optional[str]
    opens_at: Optional[str]
    closes_at: Optional[str]
    capacity: Optional[int]

    @validator('opens_at', 'closes_at')
    def check_time_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM.")
        return v

    @validator('capacity')
    def capacity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("السعة يجب أن تكون أكبر من صفر.")
        return v

class UserRegister(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    password_confirmation: str

# نقطة اختبار
@app.get("/ok")
async def ok():
    return {"status": "success", "message": "The API is working."}

# المطاعم - قراءة الكل مع فلاتر
@app.get("/restaurants")
def get_restaurants(
    area: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant)
    if area:
        query = query.filter(Restaurant.area == area)
    if cuisine:
        query = query.filter(Restaurant.cuisine == cuisine)

    restaurants = query.all()
    return {
        "status": "success",
        "data": [
            {
                "id": r.id,
                "name": r.name,
                "area": r.area,
                "cuisine": r.cuisine,
                "opens_at": r.opens_at.strftime("%H:%M"),
                "closes_at": r.closes_at.strftime("%H:%M"),
                "capacity": r.capacity,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat()
            } for r in restaurants
        ]
    }

# المطاعم - قراءة مطعم واحد
@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")
    return {
        "status": "success",
        "data": {
            "id": restaurant.id,
            "name": restaurant.name,
            "area": restaurant.area,
            "cuisine": restaurant.cuisine,
            "opens_at": restaurant.opens_at.strftime("%H:%M"),
            "closes_at": restaurant.closes_at.strftime("%H:%M"),
            "capacity": restaurant.capacity,
            "created_at": restaurant.created_at.isoformat(),
            "updated_at": restaurant.updated_at.isoformat()
        }
    }

# المطاعم - إنشاء مطعم
@app.post("/restaurants", status_code=201)
async def create_restaurant(restaurant: RestaurantCreate = Body(...), db: Session = Depends(get_db)):
    opens_time = datetime.strptime(restaurant.opens_at, "%H:%M").time()
    closes_time = datetime.strptime(restaurant.closes_at, "%H:%M").time()

    if opens_time >= closes_time:
        raise HTTPException(status_code=400, detail="وقت الفتح يجب أن يكون قبل وقت الإغلاق.")

    new_restaurant = Restaurant(
        name=restaurant.name,
        area=restaurant.area,
        cuisine=restaurant.cuisine,
        opens_at=opens_time,
        closes_at=closes_time,
        capacity=restaurant.capacity,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return {
        "status": "success",
        "data": {
            "id": new_restaurant.id,
            "name": new_restaurant.name
        }
    }

# المطاعم - تحديث مطعم
@app.put("/restaurants/{restaurant_id}")
async def update_restaurant(restaurant_id: int, restaurant_update: RestaurantUpdate = Body(...), db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    name = restaurant_update.name or restaurant.name
    area = restaurant_update.area or restaurant.area
    cuisine = restaurant_update.cuisine or restaurant.cuisine
    opens_at = restaurant_update.opens_at or restaurant.opens_at.strftime("%H:%M")
    closes_at = restaurant_update.closes_at or restaurant.closes_at.strftime("%H:%M")
    capacity = restaurant_update.capacity if restaurant_update.capacity is not None else restaurant.capacity

    opens_time = datetime.strptime(opens_at, "%H:%M").time()
    closes_time = datetime.strptime(closes_at, "%H:%M").time()

    if opens_time >= closes_time:
        raise HTTPException(status_code=400, detail="وقت الفتح يجب أن يكون قبل وقت الإغلاق.")
    if capacity <= 0:
        raise HTTPException(status_code=400, detail="السعة يجب أن تكون أكبر من صفر.")

    restaurant.name = name
    restaurant.area = area
    restaurant.cuisine = cuisine
    restaurant.opens_at = opens_time
    restaurant.closes_at = closes_time
    restaurant.capacity = capacity
    restaurant.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(restaurant)

    return {"status": "success", "message": "تم تحديث المطعم بنجاح"}

# المطاعم - حذف مطعم
@app.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    db.delete(restaurant)
    db.commit()
    return {"status": "success", "message": "تم حذف المطعم بنجاح"}

# تسجيل مستخدم جديد
@app.post("/register", status_code=201)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if user.password != user.password_confirmation:
        return JSONResponse(status_code=400, content={"status": "error", "message": "كلمتا المرور غير متطابقتين."})

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return JSONResponse(status_code=409, content={"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل."})

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    token = secrets.token_hex(16)

    new_user = User(fullname=user.fullname, email=user.email, password=hashed_password, token=token, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(status_code=201, content={
        "status": "ok",
        "fullname": new_user.fullname,
        "email": new_user.email,
        "token": new_user.token
    })

# تسجيل الدخول
@app.post("/login")
async def login_user(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return JSONResponse(status_code=400, content={"status": "error", "message": "البريد الإلكتروني وكلمة المرور مطلوبة."})

    user = db.query(User).filter(User.email == email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        token = secrets.token_hex(16)
        user.token = token
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "message": "تم تسجيل الدخول بنجاح",
            "email": email,
            "token": token,
            "last_login": user.last_login.isoformat()
        })
    return JSONResponse(status_code=401, content={"status": "error", "message": "بيانات الدخول غير صحيحة"})

# عرض ملف المستخدم حسب التوكن (Authorization Bearer Token)
@app.get("/profile")
async def get_profile(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="الرمز غير موجود أو غير صالح.")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="الرمز غير موجود أو غير صالح.")
    
    token = parts[1].strip()
    user = db.query(User).filter(User.token == token).first()
    
    if user:
        return {
            "status": "success",
            "data": {
                "fullname": user.fullname,
                "email": user.email,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }
    
    raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي.")

def get_current_user(authorization: Optional[str], db: Session):
    if not authorization:
        raise HTTPException(status_code=401, detail="الرمز غير موجود.")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="صيغة التوكن غير صحيحة.")

    token = parts[1]
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="توكن غير صالح أو غير موجود.")

    return user


# حالة الحجز (enum)
class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"

# موديل لإنشاء حجز جديد
class BookingCreate(BaseModel):
    restaurant_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    people: conint(gt=0)

    @validator('date')
    def validate_date(cls, v):
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
            if d < datetime.utcnow().date():
                raise ValueError("لا يمكن الحجز في تاريخ ماضٍ.")
            return v
        except:
            raise ValueError("صيغة التاريخ يجب أن تكون YYYY-MM-DD.")

    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M").time()
            return v
        except:
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM.")

# موديل لتحديث الحجز (جزئي)
class BookingUpdate(BaseModel):
    date: Optional[str]
    time: Optional[str]
    people: Optional[conint(gt=0)]

    @validator('date')
    def validate_date(cls, v):
        if v is None:
            return v
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
            if d < datetime.utcnow().date():
                raise ValueError("لا يمكن الحجز في تاريخ ماضٍ.")
            return v
        except:
            raise ValueError("صيغة التاريخ يجب أن تكون YYYY-MM-DD.")

    @validator('time')
    def validate_time(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M").time()
            return v
        except:
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM.")

# إنشاء حجز جديد
@app.post("/bookings", status_code=201)
async def create_booking(
    booking: BookingCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(booking.time, "%H:%M").time()

    if booking_date == datetime.utcnow().date() and booking_time <= datetime.utcnow().time():
        raise HTTPException(status_code=400, detail="لا يمكن الحجز في وقت ماضٍ.")

    if booking_time < restaurant.opens_at or booking_time >= restaurant.closes_at:
        raise HTTPException(status_code=400, detail="الوقت خارج ساعات عمل المطعم.")

    existing_bookings = db.query(Booking).filter(
        Booking.restaurant_id == restaurant.id,
        Booking.date == booking_date,
        Booking.time == booking_time,
        Booking.status == BookingStatus.confirmed
    ).all()

    total_people = sum(b.people for b in existing_bookings) + booking.people
    if total_people > restaurant.capacity:
        raise HTTPException(status_code=400, detail="السعة غير كافية لهذا الوقت.")

    new_booking = Booking(
        restaurant_id=restaurant.id,
        user_id=user.id,
        date=booking_date,
        time=booking_time,
        people=booking.people,
        status=BookingStatus.confirmed
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"status": "success", "booking_id": new_booking.id}

# استعراض كل حجوزات المستخدم
@app.get("/bookings")
def list_user_bookings(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return {
        "status": "success",
        "data": [{
            "id": b.id,
            "restaurant_id": b.restaurant_id,
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status.value,
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        } for b in bookings]
    }

# استعراض حجز معين
@app.get("/bookings/{booking_id}")
def get_booking_by_id(booking_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")
    return {
        "status": "success",
        "data": {
            "id": booking.id,
            "restaurant_id": booking.restaurant_id,
            "date": booking.date.isoformat(),
            "time": booking.time.strftime("%H:%M"),
            "people": booking.people,
            "status": booking.status.value,
            "created_at": booking.created_at.isoformat(),
            "updated_at": booking.updated_at.isoformat()
        }
    }

# تحديث الحجز
@app.put("/bookings/{booking_id}")
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")

    date_val = booking_update.date or booking.date.isoformat()
    time_val = booking_update.time or booking.time.strftime("%H:%M")
    people_val = booking_update.people if booking_update.people is not None else booking.people

    new_date = datetime.strptime(date_val, "%Y-%m-%d").date()
    new_time = datetime.strptime(time_val, "%H:%M").time()

    if new_date == datetime.utcnow().date() and new_time <= datetime.utcnow().time():
        raise HTTPException(status_code=400, detail="لا يمكن الحجز في وقت ماضٍ.")

    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if new_time < restaurant.opens_at or new_time >= restaurant.closes_at:
        raise HTTPException(status_code=400, detail="الوقت خارج ساعات عمل المطعم.")

    existing_bookings = db.query(Booking).filter(
        Booking.restaurant_id == restaurant.id,
        Booking.date == new_date,
        Booking.time == new_time,
        Booking.status == BookingStatus.confirmed,
        Booking.id != booking.id
    ).all()

    total_people = sum(b.people for b in existing_bookings) + people_val
    if total_people > restaurant.capacity:
        raise HTTPException(status_code=400, detail="السعة غير كافية لهذا الوقت.")

    booking.date = new_date
    booking.time = new_time
    booking.people = people_val
    db.commit()
    db.refresh(booking)

    return {"status": "success", "message": "تم تحديث الحجز بنجاح"}

# إلغاء الحجز (تغيير الحالة)
@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")
    booking.status = BookingStatus.cancelled
    db.commit()
    return {"status": "success", "message": "تم إلغاء الحجز بنجاح"}





