import os
import secrets
from datetime import datetime, date as date_type, time as time_type
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
from fastapi import Request, Depends
from emails import send_welcome_email, send_booking_confirmation, send_booking_cancellation
from fuzzywuzzy import fuzz
from datetime import date
from sqlalchemy import func, and_, or_









# تحميل المتغيرات من ملف .env
load_dotenv()

# إنشاء Limiter
limiter = Limiter(key_func=get_remote_address)


# إنشاء التطبيق
app = FastAPI()
# مفتاح سري لتشفير بيانات الجلسة (غيره لمفتاح قوي)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")

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
def booking_page(request: Request, restaurant_id: int):
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
    limit: Optional[int] = Query(3),
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


# حالة الحجز (enum)
class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"

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
    def validate_time(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M").time()
            return v
        except ValueError:
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
    request: Request,
    db: Session = Depends(get_db)
):
    print(request.session)
    
    # الحصول على المستخدم الحالي من الجلسة
    user = get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="يجب تسجيل الدخول للحجز." if booking.lang == 'ar' else "You must log in to book."
        )

    # التحقق من وجود المطعم
    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="المطعم غير موجود." if booking.lang == 'ar' else "Restaurant not found."
        )

    # تحويل التاريخ والوقت إلى كائنات datetime
    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(booking.time, "%H:%M").time()

    # منع الحجز في وقت ماضي لنفس اليوم
    if booking_date == datetime.now().date() and booking_time <= datetime.now().time(): 
        raise HTTPException(
            status_code=400,
            detail="لا يمكن الحجز في وقت ماضٍ اليوم." if booking.lang == 'ar' else "Cannot book in past hour."
        )

    # التأكد من أن وقت الحجز داخل ساعات عمل المطعم
    if booking_time < restaurant.opens_at or booking_time >= restaurant.closes_at:
        raise HTTPException(
            status_code=400,
            detail="الوقت خارج ساعات عمل المطعم." if booking.lang == 'ar' else "Booking time is outside restaurant hours."
        )

    # حساب إجمالي عدد الأشخاص في نفس الوقت للتأكد من السعة
    existing_bookings = db.query(Booking).filter(
        Booking.restaurant_id == restaurant.id,
        Booking.date == booking_date,
        Booking.time == booking_time,
        Booking.status == BookingStatus.confirmed
    ).all()

    total_people = sum(b.people for b in existing_bookings) + booking.people
    if total_people > restaurant.capacity:
        raise HTTPException(
            status_code=400,
            detail="السعة غير كافية لهذا الوقت." if booking.lang == 'ar' else "Not enough capacity for this time."
        )

    # إنشاء الحجز وربطه بالمستخدم
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

    # 🔔 إرسال إيميل تأكيد الحجز
    send_booking_confirmation(
    user_name=user.fullname,
    user_email=user.email,
    booking_id=new_booking.id,
    date=new_booking.date.strftime("%Y-%m-%d"),
    time=new_booking.time.strftime("%H:%M"),
    service_name=new_booking.restaurant.name  # اسم المطعم
    )


    # إعادة رد JSON كامل ليتم عرضه في frontend
    return {
        "status": "success",
        "booking_id": new_booking.id,
        "date": new_booking.date.strftime("%Y-%m-%d"),
        "time": new_booking.time.strftime("%H:%M"),
        "people": new_booking.people
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
        .order_by(Booking.date.desc())
        .all()
    )

    data = []
    for b in bookings:
        if not b.restaurant:
            restaurant_name = "غير معروف"
        else:
            # ✅ اختيار الاسم حسب اللغة
            restaurant_name = b.restaurant.name_en if lang == "en" else b.restaurant.name

        data.append({
            "id": b.id,
            "restaurant_name": restaurant_name,
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status,
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        })

    return {"status": "success", "data": data}


# عرض جميع الحجوزات - خاص بالأدمن فقط
@app.get("/api/admin/bookings")
def get_admin_bookings(
    lang: str = Query("ar"), 
    db: Session = Depends(get_db),
    user: User = Depends(admin_required)
):
    bookings = db.query(Booking).all()
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

    return {"status": "success", "data": result}


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



FastAPI
