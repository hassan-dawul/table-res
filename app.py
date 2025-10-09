import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends, Body
from fastapi.responses import JSONResponse
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
import secrets
import jwt

from pydantic import BaseModel, validator, EmailStr
from db import SessionLocal, engine, Base
from models import User, Restaurant, Booking, BookingStatus
from enum import Enum
from pydantic import conint
from datetime import date as date_type, time as time_type
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.responses import RedirectResponse





# تحميل المتغيرات من ملف .env
load_dotenv()

# إنشاء Limiter
limiter = Limiter(key_func=get_remote_address)

# إنشاء التطبيق
app = FastAPI()

# إنشاء التطبيق
app = FastAPI()
# مفتاح سري لتشفير بيانات الجلسة (غيره لمفتاح قوي)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")

app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")  # ضع مفتاح سري قوي هنا

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
)


# مفتاح سري لتشفير بيانات الجلسة (غيره لمفتاح قوي)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")

app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")  # ضع مفتاح سري قوي هنا

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")  
# ربط ملفات static (مثل css و js) لتقديمها

templates = Jinja2Templates(directory="templates")

# تعيين limiter في app.state
app.state.limiter = limiter


# إضافة middleware الخاص بـ slowapi
app.add_middleware(SlowAPIMiddleware)

# معالج خطأ تجاوز الحد (rate limit)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "لقد وصلت للحد المسموح من المحاولات، يرجى الانتظار دقيقة ثم المحاولة مجدداً."
        }
    )

# هنا بعدين تضيف باقي الراوتات والدوال مثل تسجيل الدخول، الحجز، الخ...




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

# دالة لتشفير كلمة السر
def hash_password(password: str) -> str:  # NEW
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# دالة لفك تشفير كلمة السر
def verify_password(plain_password: str, hashed_password: str) -> bool:  # NEW
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# دالة لتوليد JWT
def create_access_token(data: dict, expires_delta: Optional[int] = None):  # NEW
    import datetime
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta or 30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("ACCESS_TOKEN_SECRET"), algorithm="HS256")
    return encoded_jwt
# دالة التحقق من صلاحية الأدمن
def admin_required(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    user = get_current_user(authorization, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="غير مصرح لك بالوصول إلى هذا المورد.")
    return user

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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    # 🔒 إذا المستخدم مسجل دخول، نحوله للملف الشخصي
    if request.session.get("user"):
        return RedirectResponse(url="/profile", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    # 🔒 إذا المستخدم مسجل دخول، نحوله للملف الشخصي
    if request.session.get("user"):
        return RedirectResponse(url="/profile", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    if 'user' not in request.session:
        return RedirectResponse("/login")
    return templates.TemplateResponse("profile.html", {"request": request})

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
async def create_restaurant(
    restaurant: RestaurantCreate = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(admin_required)  # NEW: السماح للادمن فقط
):
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
async def update_restaurant(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(admin_required)  # NEW: السماح للادمن فقط
):
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
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required)  # NEW: فقط الادمن يمكنه حذف المطاعم
):
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
    token = secrets.token_hex(16)  # NEW: إنشاء توكن عشوائي لتوثيق المستخدم

    new_user = User(
        fullname=user.fullname,
        email=user.email,
        password=hashed_password,
        token=token,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        role="user"  # NEW: تعيين الدور الافتراضي للمستخدم (مستخدم عادي)
    )
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
@limiter.limit("5/minute")
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
        
        # بعد التأكد من bcrypt.checkpw
        request.session['user'] = user.token  # تخزين التوكن في الجلسة

        return JSONResponse(status_code=200, content={
            "status": "ok",
            "message": "تم تسجيل الدخول بنجاح",
            "email": email,
            "token": token,
            "last_login": user.last_login.isoformat()
        })
    return JSONResponse(status_code=400, content={"status": "error", "message": "بيانات الدخول غير صحيحة"})


# عرض ملف المستخدم حسب التوكن (Authorization Bearer Token)
@app.get("/profile")
async def get_profile(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
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
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "role": user.role  # NEW: إضافة عرض الدور
            }
        }

    raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي.")

@app.get("/user")
def get_user(request: Request, db: Session = Depends(get_db)):
    token = request.session.get('user')
    if not token:
        return {"status": "error", "message": "المستخدم غير مسجل"}
    
    user = db.query(User).filter(User.token == token).first()
    if not user:
        return {"status": "error", "message": "توكن غير صالح"}

    return {
        "status": "success",
        "data": {
            "fullname": user.fullname,
            "email": user.email,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    }

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()  # 🧹 مسح الجلسة بالكامل
    return RedirectResponse(url="/login", status_code=303)


# دالة مساعدة لجلب المستخدم الحالي من التوكن
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
    people: conint(gt=0)  # pyright: ignore[reportInvalidTypeForm] # NEW: التحقق من أن عدد الأشخاص أكبر من صفر

    @validator('date')
    def validate_date(cls, v):
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
            if d < datetime.utcnow().date():
                raise ValueError("لا يمكن الحجز في تاريخ ماضٍ.")  # NEW: منع الحجز في الماضي
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
    people: Optional[conint(gt=0)]  # pyright: ignore[reportInvalidTypeForm] # NEW: التحقق من أن عدد الأشخاص أكبر من صفر

    @validator('date')
    def validate_date(cls, v):
        if v is None:
            return v
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
            if d < datetime.utcnow().date():
                raise ValueError("لا يمكن الحجز في تاريخ ماضٍ.")  # NEW: منع التحديث لتاريخ ماضي
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
    user = get_current_user(authorization, db)  # NEW: التأكد من توكن المستخدم لجلب بياناته

    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(booking.time, "%H:%M").time()

    # NEW: منع الحجز في وقت ماضي في نفس اليوم
    if booking_date == datetime.utcnow().date() and booking_time <= datetime.utcnow().time():
        raise HTTPException(status_code=400, detail="لا يمكن الحجز في وقت ماضٍ.")

    # NEW: التأكد من أن وقت الحجز داخل ساعات عمل المطعم
    if booking_time < restaurant.opens_at or booking_time >= restaurant.closes_at:
        raise HTTPException(status_code=400, detail="الوقت خارج ساعات عمل المطعم.")

    # NEW: حساب إجمالي عدد الأشخاص في نفس الوقت للتأكد من السعة
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
        user_id=user.id,  # NEW: ربط الحجز بالمستخدم الحالي
        date=booking_date,
        time=booking_time,
        people=booking.people,
        status=BookingStatus.confirmed  # NEW: تعيين حالة الحجز مؤكدة بشكل افتراضي
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"status": "success", "booking_id": new_booking.id}

# استعراض كل حجوزات المستخدم
@app.get("/bookings")
def list_user_bookings(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)  # NEW: التحقق من توكن المستخدم لجلب بياناته
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return {
        "status": "success",
        "data": [{
            "id": b.id,
            "restaurant_id": b.restaurant_id,
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status.value,  # NEW: عرض حالة الحجز (confirmed أو cancelled)
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        } for b in bookings]
    }

# استعراض حجز معين
@app.get("/bookings/{booking_id}")
def get_booking_by_id(booking_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)  # NEW: التحقق من توكن المستخدم
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
            "status": booking.status.value,  # NEW: عرض حالة الحجز
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
    user = get_current_user(authorization, db)  # NEW: التحقق من توكن المستخدم
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")

    date_val = booking_update.date or booking.date.isoformat()
    time_val = booking_update.time or booking.time.strftime("%H:%M")
    people_val = booking_update.people if booking_update.people is not None else booking.people

    new_date = datetime.strptime(date_val, "%Y-%m-%d").date()
    new_time = datetime.strptime(time_val, "%H:%M").time()

    # NEW: منع تحديث الحجز إلى وقت ماضي في نفس اليوم
    if new_date == datetime.utcnow().date() and new_time <= datetime.utcnow().time():
        raise HTTPException(status_code=400, detail="لا يمكن الحجز في وقت ماضٍ.")

    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()

    # NEW: التحقق من أن وقت الحجز داخل ساعات عمل المطعم
    if new_time < restaurant.opens_at or new_time >= restaurant.closes_at:
        raise HTTPException(status_code=400, detail="الوقت خارج ساعات عمل المطعم.")

    # NEW: التأكد من أن السعة متاحة عند التحديث (باستثناء الحجز الحالي)
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
    user = get_current_user(authorization, db)  # NEW: التحقق من توكن المستخدم
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")
    booking.status = BookingStatus.cancelled  # NEW: تغيير حالة الحجز إلى ملغي بدل الحذف
    db.commit()
    return {"status": "success", "message": "تم إلغاء الحجز بنجاح"}




FastAPI
