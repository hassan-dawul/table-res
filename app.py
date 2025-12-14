import os
import secrets
import json
from datetime import datetime, date as date_type, time as time_type, timedelta
from enum import Enum
from typing import Optional, List

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Query, Header, Depends, Body
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.orm import Session, joinedload

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from pydantic import BaseModel, validator, EmailStr, conint

from db import SessionLocal, engine, Base, get_db
from models import User, Restaurant, Booking, BookingStatus, ContactMessage
from emails import send_welcome_email, send_booking_confirmation, send_booking_cancellation
from fuzzywuzzy import fuzz, process
from datetime import date
from sqlalchemy import func, and_, or_
import stripe
from apscheduler.schedulers.background import BackgroundScheduler
from langdetect import detect, DetectorFactory






STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
BASE_URL = os.getenv("BASE_URL")

stripe.api_key = STRIPE_SECRET_KEY




# تحميل المتغيرات من ملف .env
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


# إنشاء Limiter
limiter = Limiter(key_func=get_remote_address)


# إنشاء التطبيق
app = FastAPI()
# مفتاح سري لتشفير بيانات الجلسة (غيره لمفتاح قوي)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")  # ضع مفتاح سري قوي هنا


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
)


app.mount("/static", StaticFiles(directory="static"), name="static")  
# ربط ملفات static (مثل css و js) لتقديمها

templates = Jinja2Templates(directory="templates")

# تعيين limiter في app.state
app.state.limiter = limiter

@app.get("/booking/{restaurant_id}", response_class=HTMLResponse)
def booking_page(request: Request, restaurant_id: int, db: Session = Depends(get_db)):
    # جلب المطعم من قاعدة البيانات
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return HTMLResponse("<h2>المطعم غير موجود!</h2>")

    # تمرير اللغة من الجلسة
    lang = request.session.get("lang", "ar")

    return templates.TemplateResponse(
        "booking.html",
        
                {"request": request, "restaurant_id": restaurant_id}

    )

@app.get("/admin/bookings", response_class=HTMLResponse)
def admin_bookings_page(request: Request, db: Session = Depends(get_db)):
    user = admin_required(request, db)  # تتحقق من صلاحية الأدمن
    return templates.TemplateResponse("admin_bookings.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/how", response_class=HTMLResponse)
async def how_page(request: Request):
    return templates.TemplateResponse("how.html", {"request": request})





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

translations = {
    "ar": {
        "open-now": "المطعم مفتوح الآن",
        "closed-now": "المطعم مغلق الآن",
        "capacity-info": "السعة: {capacity} شخص",
        "most-booked": "الأكثر حجزًا",
        "book-now-btn": "احجز الآن",
            "chat-title": "الشات",
    "ask-restaurant": "اسأل عن مطعم...",   
    "send-btn": "إرسال",                    
    "user-prefix": "أنت",                
    "bot-error": "بوت: حدث خطأ، حاول مرة أخرى.",

    },
    "en": {
        "open-now": "Restaurant is open now",
        "closed-now": "Restaurant is closed now",
        "capacity-info": "Capacity: {capacity} people",
        "most-booked": "Most booked",
        "book-now-btn": "Book Now",
        
    }
}



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
    request: Request,
    db: Session = Depends(get_db)
    ) -> User:
    user = get_current_user_from_session(request, db) 
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
async def index(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = get_current_user_from_session(request, db)
    except HTTPException:
        current_user = None  # إذا ما فيه جلسة مسجل دخول، خلي current_user None

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "current_user": current_user}
    )


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

@app.get("/pay")
async def pay(request: Request, s: str = Query(...), db: Session = Depends(get_db)):
    # booking = db.query(Booking).filter(Booking.id == booking_id).first()
    # if not booking:
    #     return HTMLResponse("<h2>❌ الحجز غير موجود</h2>")
    return templates.TemplateResponse("pay.html", {
        "request": request,
        "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
        "secret": s
    })

class ChatMessage(BaseModel):
    message: str
    lang: str = "ar"  # ar أو en


@app.get("/chat")
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})



# نقطة اختبار
@app.get("/ok")
async def ok():
    return {"status": "success", "message": "The API is working."}

# 🔹 دالة لتوحيد النصوص وإزالة الهمزات
def normalize_text(text: str):
    return (
        (text or "")
        .replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ة", "ه")
        .replace("ى", "ي")
        .lower()
        .strip()
    )

# 🔹 جلب جميع المطاعم مع بحث ذكي وفلاتر + عدد الحجز اليوم + ترتيب حسب أعلى الحجوزات
@app.get("/restaurants")
def get_restaurants(
    search: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    lang: str = Query("ar"),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    today = date.today()

    # جدول المطاعم + عدد الحجوزات اليوم
    query = (
        db.query(
            Restaurant,
            func.count(Booking.id).label("today_bookings")
        )
        .outerjoin(
            Booking,
            (Booking.restaurant_id == Restaurant.id) & (Booking.date == today)
        )
    )

    # ===== فلترة =====
    if area:
        query = query.filter(
            or_(
                Restaurant.area.ilike(f"%{area}%"),
                Restaurant.area_en.ilike(f"%{area}%")
            )
        )
    if cuisine:
        query = query.filter(
            or_(
                Restaurant.cuisine.ilike(f"%{cuisine}%"),
                Restaurant.cuisine_en.ilike(f"%{cuisine}%")
            )
        )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Restaurant.name.ilike(search_pattern),
                Restaurant.name_en.ilike(search_pattern),
                Restaurant.area.ilike(search_pattern),
                Restaurant.area_en.ilike(search_pattern),
                Restaurant.cuisine.ilike(search_pattern),
                Restaurant.cuisine_en.ilike(search_pattern)
            )
        )

    # تجميع وعدّ الحجوزات اليوم لكل مطعم
    query = query.group_by(Restaurant.id)

    # ترتيب حسب أكثر عدد حجوزات اليوم
    query = query.order_by(func.count(Booking.id).desc())

    # حد أقصى
    if limit:
        query = query.limit(limit)

    results = query.all()

    # تحويل النتائج للـ JSON مع اللغة
    data = [
        {
            "id": r.Restaurant.id,
            "name": r.Restaurant.name if lang == "ar" else r.Restaurant.name_en or r.Restaurant.name,
            "area": r.Restaurant.area if lang == "ar" else r.Restaurant.area_en or r.Restaurant.area,
            "cuisine": r.Restaurant.cuisine if lang == "ar" else r.Restaurant.cuisine_en or r.Restaurant.cuisine,
            "opens_at": r.Restaurant.opens_at.strftime("%H:%M"),
            "closes_at": r.Restaurant.closes_at.strftime("%H:%M"),
            "capacity": r.Restaurant.capacity,
            "today_bookings": r.today_bookings,
            "created_at": r.Restaurant.created_at.isoformat(),
            "updated_at": r.Restaurant.updated_at.isoformat()
        } for r in results
    ]

    return {"status": "success", "data": data}


# ====== المطاعم - جلب قائمة الفلاتر ======
@app.get("/restaurants/filters")
def get_restaurant_filters(lang: str = "ar", db: Session = Depends(get_db)):
    if lang == "en":
        cuisines = db.query(Restaurant.cuisine_en).distinct().all()
        areas = db.query(Restaurant.area_en).distinct().all()
    else:
        cuisines = db.query(Restaurant.cuisine).distinct().all()
        areas = db.query(Restaurant.area).distinct().all()

    # flatten من tuples إلى قائمة بسيطة
    cuisines = [c[0] for c in cuisines if c[0]]
    areas = [a[0] for a in areas if a[0]]

    return {
        "status": "success",
        "filters": {
            "cuisines": cuisines,
            "areas": areas
        }
    }


# ======= صفحة المطاعم (HTML) =======
@app.get("/restaurants_page")
def restaurants_page(request: Request):
    return templates.TemplateResponse("restaurants.html", {"request": request})


from fastapi import Query

@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(
    restaurant_id: int,
    lang: str = Query("ar"),  # اللغة الافتراضية عربي
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")
    
    return {
        "status": "success",
        "data": {
            "id": restaurant.id,
            "name": restaurant.name if lang == "ar" else restaurant.name_en or restaurant.name,
            "area": restaurant.area if lang == "ar" else restaurant.area_en or restaurant.area,
            "cuisine": restaurant.cuisine if lang == "ar" else restaurant.cuisine_en or restaurant.cuisine,
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

    send_welcome_email(new_user.fullname, new_user.email)




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
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "البريد الإلكتروني وكلمة المرور مطلوبة."}
        )

    # البحث عن المستخدم في قاعدة البيانات
    user = db.query(User).filter(User.email == email).first()

    # التحقق من كلمة المرور
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # إنشاء توكن جديد
        token = secrets.token_hex(16)
        user.token = token
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

        # ✅ تخزين التوكن + user_id + role في الجلسة
        request.session['user'] = user.token
        request.session['user_id'] = user.id
        request.session['role'] = user.role  # مهم للأدمن

        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": "تم تسجيل الدخول بنجاح",
                "email": email,
                "token": token,
                "role": user.role,
                "last_login": user.last_login.isoformat()
            }
        )

    # بيانات الدخول غير صحيحة
    return JSONResponse(
        status_code=400, 
        content={"status": "error", "message": "بيانات الدخول غير صحيحة"}
    )


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


def get_current_user_from_session(request: Request, db: Session):
    # أخذ التوكن من الجلسة
    token: Optional[str] = request.session.get('user')
    print('my token', token)
    
    if not token:
        raise HTTPException(status_code=401, detail="الرمز غير موجود في الجلسة.")

    # البحث عن المستخدم بالتوكن في قاعدة البيانات
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="توكن غير صالح أو غير موجود.")

    return user

# موديل لإنشاء حجز جديد
class BookingCreate(BaseModel):
    lang: str
    restaurant_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    people: conint(gt=0)  # pyright: ignore[reportInvalidTypeForm] # NEW: التحقق من أن عدد الأشخاص أكبر من صفر

    @validator('date')
    def validate_date(cls, v, values):
        print(values)
        lang = values.get("lang", "ar")
        
        if v is None:
            return v

        # ✅ تحقق من الصيغة
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ يجب أن تكون YYYY-MM-DD.")
        
        # ✅ تحقق من أن التاريخ ليس ماضيًا
        if d < datetime.utcnow().date():
            raise HTTPException(status_code=400, detail="لا يمكن الحجز في تاريخ ماضٍ." if lang == 'ar' else "Cannot book a past date")
      
        return v

    @validator('time')
    def validate_time(cls, v, values):
        if v is None:
            return v

        # تحقق من صيغة الوقت
        try:
            booking_time = datetime.strptime(v, "%H:%M").time()
        except ValueError:
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM.")

        # جلب التاريخ من نفس الموديل
        booking_date_str = values.get("date")
        lang = values.get("lang", "ar")

        # إذا المستخدم كتب وقت فقط بدون تاريخ → نرجّع بدون تحقق إضافي
        if not booking_date_str:
            return v

        # تحويل التاريخ
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        except:
            return v  # التاريخ سيُرفض لاحقاً في validator التاريخ

        # الوقت الحالي
        now = datetime.utcnow()

        # التحقق من أنه نفس اليوم
        if booking_date == now.date():
            if booking_time < now.time():
                raise HTTPException(
                    status_code=400,
                    detail="لا يمكن الحجز لوقت مضى اليوم." if lang == "ar" else "Cannot book a past time today"
                )

        return v



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
        
@app.post("/bookings", status_code=201)
async def create_booking(booking: BookingCreate, request: Request, db: Session = Depends(get_db)):
    lang = booking.lang if hasattr(booking, "lang") else "ar"  # جلب لغة المستخدم من البيانات المرسلة

    # مثال: منع الحجز بتاريخ ماضي
    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    if booking_date < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="لا يمكن الحجز في تاريخ ماضٍ." if lang == 'ar' else "Cannot book a past date"
        )

    # مثال: التحقق من تسجيل الدخول
    try:
        user = get_current_user_from_session(request, db)
    except HTTPException:
        raise HTTPException(
            status_code=401,
            detail="يجب تسجيل الدخول لإتمام الحجز." if lang == 'ar' else "You must log in to complete the booking."
        )
    # ===== التحقق من المطعم =====
    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    # تحويل التاريخ والوقت
    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(booking.time, "%H:%M").time()

    # التحقق من السعة
    existing_bookings = db.query(Booking).filter(
        Booking.restaurant_id == restaurant.id,
        Booking.date == booking_date,
        Booking.time == booking_time,
        Booking.status == BookingStatus.confirmed
    ).all()
    total_people = sum(b.people for b in existing_bookings) + booking.people
    if total_people > restaurant.capacity:
        raise HTTPException(status_code=400, detail="السعة غير كافية لهذا الوقت.")

    # إنشاء الحجز مؤقت
    new_booking = Booking(
        restaurant_id=restaurant.id,
        user_id=user.id,
        date=booking_date,
        time=booking_time,
        people=booking.people,
        status=BookingStatus.pending
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # حساب السعر
    amount = booking.people * 10 * 100  # 10 ريال × 100 سنت

    # إنشاء جلسة Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'sar',
                'product_data': {
                    'name': f"حجز مطعم {restaurant.name} بتاريخ {booking.date}"
                },
                'unit_amount': amount
            },
            'quantity': 1
        }],
        mode='payment',
        ui_mode='embedded',
        metadata={"booking_id": new_booking.id},
        return_url=f"{BASE_URL}/booking-success?session_id={{CHECKOUT_SESSION_ID}}",
        customer_email=user.email
    )

    new_booking.client_secret = session.client_secret
    db.commit()
    db.refresh(new_booking)

    return {
        "status": "success",
        "booking_id": new_booking.id,
        "client_secret": session.client_secret
    }

# استعراض كل حجوزات المستخدم
@app.get("/api/bookings")
def list_user_bookings(
    request: Request,
    db: Session = Depends(get_db),
    lang: str = Query("ar")  # ✅ اللغة تجي من الرابط
):
    print("📢 اللغة المستلمة:", lang)

    user = get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="يجب تسجيل الدخول لرؤية الحجوزات.")

    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.restaurant))
        .filter(Booking.user_id == user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    data = []
    for b in bookings:
        if not b.restaurant:
            restaurant_name = "غير معروف"
        else:
            restaurant_name = b.restaurant.name_en if lang == "en" else b.restaurant.name

        booking_data = {
            "id": b.id,
            "restaurant_name": restaurant_name,
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status,
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        }

        # ✅ إذا الحجز Pending، أضف client_secret لتمكين زر "ادفع الآن"
        if b.status == BookingStatus.pending and hasattr(b, "client_secret"):
            booking_data["client_secret"] = b.client_secret

        data.append(booking_data)

    return {"status": "success", "data": data}



# عرض جميع الحجوزات - خاص بالأدمن فقط
@app.get("/api/admin/bookings")
def get_admin_bookings(
    page: int = Query(1, ge=1),        # رقم الصفحة
    per_page: int = Query(40, ge=1),   # عدد الحجوزات لكل صفحة
    lang: str = Query("ar"), 
    db: Session = Depends(get_db),
    user: User = Depends(admin_required)
):
    query = db.query(Booking).order_by(Booking.created_at.desc())
    total = query.count()
    bookings = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for b in bookings:
        restaurant = db.query(Restaurant).filter(Restaurant.id == b.restaurant_id).first()
        u = db.query(User).filter(User.id == b.user_id).first()
        restaurant_name = restaurant.name if lang == "ar" else restaurant.name_en

        result.append({
            "id": b.id,
            "restaurant_name": restaurant_name,
            "user_name": u.fullname if u else "غير معروف",
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status,
        })

    return {
        "status": "success",
        "data": result,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

# استعراض حجز معين
@app.get("/bookings/{booking_id}")
def get_booking_by_id(booking_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = get_current_user_from_session(Request, db)
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
    user =get_current_user_from_session (authorization, db)  
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
@app.delete("/api/bookings/{booking_id}")
def cancel_booking(booking_id: int, request: Request, db: Session = Depends(get_db)):
    # جلب المستخدم من السيشن
    user = get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="يجب تسجيل الدخول.")
    
    # جلب الحجز
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="الحجز غير موجود.")
    
    # تغيير حالة الحجز إلى ملغي
    booking.status = BookingStatus.cancelled
    db.commit()

    # جلب بيانات المطعم المرتبط بالحجز
    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    service_name = restaurant.name if restaurant else "الخدمة"

    # ✉️ إرسال إيميل إلغاء الحجز مع معالجة الأخطاء
    try:
        send_booking_cancellation(
            user_name=user.fullname,   # لاحظ استخدام fullname بدل name
            user_email=user.email,
            booking_id=booking.id,
            date=booking.date,
            time=booking.time,
            service_name=service_name
        )
    except Exception as e:
        print(f"❌ فشل إرسال إيميل الإلغاء: {e}")

    return {
        "status": "success",
        "message": "تم إلغاء الحجز بنجاح وتم إرسال إشعار عبر البريد الإلكتروني."
    }

@app.post("/contact")
async def contact_submit(request: Request):
    data = await request.json()
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")
    lang = data.get("lang", "ar")  # افتراضي عربي

    # فتح جلسة مع قاعدة البيانات
    db: Session = SessionLocal()
    try:
        new_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    finally:
        db.close()

    # ترجمة الرسالة حسب اللغة
    response_msg = (
        "تم إرسال الرسالة وحفظها في قاعدة البيانات!" if lang == "ar"
        else "Message sent successfully and saved in the database!"
    )

    return JSONResponse({"message": response_msg})

@app.get("/availability")
def check_availability(
    restaurant_id: int = Query(...),
    date: str = Query(...),
    time: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    يرجع عدد الأشخاص المتبقيين للحجز في مطعم معين بتاريخ ووقت معين.
    """

    # جلب المطعم
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # تحويل التاريخ والوقت إلى datetime
    booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(time, "%H:%M").time()

    # إذا التاريخ اليوم أو قبل والوقت مضى، لا يظهر شيء
    if booking_date < datetime.now().date() or (booking_date == datetime.now().date() and booking_time <= datetime.now().time()):
        return {
            "status": "success",
            "restaurant_id": restaurant_id,
            "date": date,
            "time": time,
            "remaining": 0  # أو "" إذا تريد يطلع فاضي
        }

    # حساب مجموع الأشخاص المحجوزين في نفس التاريخ والوقت
    booked_people = (
        db.query(func.sum(Booking.people))
        .filter(Booking.restaurant_id == restaurant_id)
        .filter(func.date(Booking.date) == date)
        .filter(Booking.time == time)
        .scalar()
    ) or 0

    remaining = max(restaurant.capacity - booked_people, 0)

    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "date": date,
        "time": time,
        "remaining": remaining
    }

# صفحة نجاح الدفع
@app.get("/booking-success", response_class=HTMLResponse)
def booking_success(
    request: Request,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    session = stripe.checkout.Session.retrieve(session_id)
    booking_id = session.metadata.get("booking_id")

    if not booking_id:
        return HTMLResponse("<h2>الحجز غير موجود!</h2>")

    booking = db.query(Booking).filter(Booking.id == int(booking_id)).first()
    if not booking:
        return HTMLResponse("<h2>الحجز غير موجود!</h2>")

    if booking.status != BookingStatus.confirmed:
        booking.status = BookingStatus.confirmed
        db.commit()
        db.refresh(booking)

        # إرسال إيميل تأكيد الحجز
        send_booking_confirmation(
            user_name=booking.user.fullname,
            user_email=booking.user.email,
            booking_id=booking.id,
            date=booking.date.strftime("%Y-%m-%d"),
            time=booking.time.strftime("%H:%M"),
            service_name=booking.restaurant.name
        )

    return templates.TemplateResponse(
    "booking-success.html",
    {"request": request, "booking": booking, "lang": request.session.get("lang", "ar")}
)



# صفحة إلغاء الدفع
@app.get("/booking-cancel", response_class=HTMLResponse)
def booking_cancel():
    return HTMLResponse("<h2>تم إلغاء الدفع.</h2>")


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    # التحقق من صحة payload وتوقيع Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # payload غير صالح
        print(f"⚠️ Invalid payload: {e}")
        return {"status": "invalid payload"}
    except stripe.error.SignatureVerificationError as e:
        # التوقيع غير صالح
        print(f"⚠️ Invalid signature: {e}")
        return {"status": "invalid signature"}
    except Exception as e:
        print(f"⚠️ Webhook error: {e}")
        return {"status": "error"}

    # التعامل مع الدفع الناجح فقط
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        booking_id = session_obj['metadata'].get('booking_id')

        if booking_id:
            db_booking = db.query(Booking).filter(Booking.id == int(booking_id)).first()
            if db_booking:
                # تحديث حالة الحجز
                db_booking.status = BookingStatus.confirmed
                db.commit()
                db.refresh(db_booking)

                # إرسال بريد التأكيد
                user = db.query(User).filter(User.id == db_booking.user_id).first()
                if user:
                    send_booking_confirmation(
                        user_name=user.fullname,
                        user_email=user.email,
                        booking_id=db_booking.id,
                        date=db_booking.date.strftime("%Y-%m-%d"),
                        time=db_booking.time.strftime("%H:%M"),
                        service_name=db_booking.restaurant.name
                    )

    return {"status": "success"}


@app.post("/create-checkout-session")
async def create_checkout_session():
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'طاولتك'},
                'unit_amount': 2000,
            },
            'quantity': 1,
        }],
        mode='payment',
        ui_mode='embedded',
        return_url='http://127.0.0.1:5000/booking-success?session_id={CHECKOUT_SESSION_ID}',
    )
    return JSONResponse({"clientSecret": session.client_secret})

@app.delete("/api/bookings/cleanup")
def cleanup_expired_bookings(db: Session = Depends(get_db)):
    expiration = datetime.utcnow() - timedelta(minutes=2)
    deleted_count = db.query(Booking).filter(
        Booking.status == BookingStatus.pending,
        Booking.created_at < expiration
    ).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted_count}

@app.get("/cities")
def get_cities(lang: str = Query("ar"), db: Session = Depends(get_db)):
    if lang == "ar":
        cities = db.query(Restaurant.area).distinct().all()
    else:
        cities = db.query(Restaurant.area_en).distinct().all()
    city_list = [c[0] for c in cities if c[0]]
    return {"status": "success", "data": city_list}


# دالة كشف اللغة
def detect_lang_simple(text):
    for c in text:
        if '\u0600' <= c <= '\u06FF':  # أي حرف عربي
            return "ar"
    return "en"

@app.post("/chatbot")
async def chatbot(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    message = data.get("message", "").strip()

    if not message:
        return {"reply": "اكتب سؤالك من فضلك"}

    # كشف اللغة تلقائيًا
    lang = detect_lang_simple(message)

    today = date.today()
    now = datetime.now().time()

    restaurants = db.query(Restaurant).all()
    results = []

    for r in restaurants:
        # اختيار الحقول حسب اللغة المكتشفة
        target_name = r.name_en if lang == "en" else r.name
        target_cuisine = r.cuisine_en if lang == "en" else r.cuisine
        target_area = r.area_en if lang == "en" else r.area

        if fuzz.partial_ratio(message.lower(), target_name.lower()) > 60 or \
           fuzz.partial_ratio(message.lower(), target_cuisine.lower()) > 60 or \
           fuzz.partial_ratio(message.lower(), target_area.lower()) > 60:
            results.append(r)

    if not results:
        return {"reply": "لم أجد مطاعم تناسب سؤالك" if lang=="ar" else "No matching restaurants found"}

    # ترتيب حسب أكثر حجوزات اليوم
    results = sorted(results, key=lambda r: db.query(Booking).filter(
        Booking.restaurant_id == r.id,
        Booking.date == today
    ).count(), reverse=True)

    # إنشاء HTML للرد
    reply_html = ""
    for r in results:
        bookings_today = db.query(Booking).filter(
            Booking.restaurant_id == r.id,
            Booking.date == today
        ).count()

        # تحديث الحقول حسب اللغة لكل مطعم
        target_name = r.name_en if lang == "en" else r.name
        target_cuisine = r.cuisine_en if lang == "en" else r.cuisine
        target_area = r.area_en if lang == "en" else r.area

        status = translations[lang]['open-now'] if r.opens_at <= now <= r.closes_at else translations[lang]['closed-now']

        reply_html += f"""
        <div style='border:1px solid #ccc; padding:8px; margin-bottom:5px; border-radius:6px; background:#f9f9f9;'>
            <strong>{target_name}</strong> - {target_area} - {target_cuisine}<br>
            {status}<br>
            {translations[lang]['capacity-info'].replace('{capacity}', str(r.capacity))}<br>
            {translations[lang]['most-booked']}: {bookings_today}<br>
            <a href='/booking/{r.id}'>{translations[lang]['book-now-btn']}</a>
        </div>
        """

    return {"reply": reply_html}

FastAPI
