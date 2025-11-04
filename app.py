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
from models import User, Restaurant, Booking, BookingStatus
from fastapi import Request, Depends
from emails import send_welcome_email, send_booking_confirmation, send_booking_cancellation






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

# المطاعم - قراءة الكل مع فلاتر
@app.get("/restaurants")
def get_restaurants(
    area: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    lang: str = Query("ar"),  # اللغة الافتراضية عربي
    limit: int = Query(3),
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant)

    if area:
        query = query.filter(Restaurant.area == area if lang=="ar" else Restaurant.area_en == area)
    if cuisine:
        query = query.filter(Restaurant.cuisine == cuisine if lang=="ar" else Restaurant.cuisine_en == cuisine)
    if search:
        query = query.filter(Restaurant.name.ilike(f"%{search}%") if lang=="ar" else Restaurant.name_en.ilike(f"%{search}%"))

    restaurants = query.limit(limit).all()

    return {
        "status": "success",
        "data": [
            {
                "id": r.id,
                "name": r.name if lang=="ar" else r.name_en or r.name,
                "area": r.area if lang=="ar" else r.area_en or r.area,
                "cuisine": r.cuisine if lang=="ar" else r.cuisine_en or r.cuisine,
                "opens_at": r.opens_at.strftime("%H:%M"),
                "closes_at": r.closes_at.strftime("%H:%M"),
                "capacity": r.capacity,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat()
            } for r in restaurants
        ]
    }


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
    restaurant_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    people: conint(gt=0)  # pyright: ignore[reportInvalidTypeForm] # NEW: التحقق من أن عدد الأشخاص أكبر من صفر

    @validator('date')
    def validate_date(cls, v):
        

        if v is None:
            return v

        # ✅ تحقق من الصيغة
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ يجب أن تكون YYYY-MM-DD.")
        
        # ✅ تحقق من أن التاريخ ليس ماضيًا
        if d < datetime.utcnow().date():
            raise HTTPException(status_code=400, detail="لا يمكن الحجز في تاريخ ماضٍ.")
      
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
        raise HTTPException(status_code=401, detail="يجب تسجيل الدخول للحجز.")

    # التحقق من وجود المطعم
    restaurant = db.query(Restaurant).filter(Restaurant.id == booking.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="المطعم غير موجود.")

    # تحويل التاريخ والوقت إلى كائنات datetime
    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    booking_time = datetime.strptime(booking.time, "%H:%M").time()

    
    # منع الحجز في وقت ماضي لنفس اليوم
    if booking.date == datetime.now().date() and booking.time <= datetime.now().time(): 
        raise HTTPException(status_code=400, detail="لا يمكن الحجز في وقت ماضٍ اليوم.") 

    # التأكد من أن وقت الحجز داخل ساعات عمل المطعم
    if booking_time < restaurant.opens_at or booking_time >= restaurant.closes_at:
        raise HTTPException(status_code=400, detail="الوقت خارج ساعات عمل المطعم.")

    # حساب إجمالي عدد الأشخاص في نفس الوقت للتأكد من السعة
    existing_bookings = db.query(Booking).filter(
        Booking.restaurant_id == restaurant.id,
        Booking.date == booking_date,
        Booking.time == booking_time,
        Booking.status == BookingStatus.confirmed
    ).all()

    total_people = sum(b.people for b in existing_bookings) + booking.people
    if total_people > restaurant.capacity:
        raise HTTPException(status_code=400, detail="السعة غير كافية لهذا الوقت.")

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
def list_user_bookings(request: Request, db: Session = Depends(get_db)):
    # الحصول على المستخدم الحالي من الجلسة
    user = get_current_user_from_session(request, db)  # احرص على تمرير request الفعلي
    if not user:
        raise HTTPException(status_code=401, detail="يجب تسجيل الدخول لرؤية الحجوزات.")

    # جلب جميع حجوزات المستخدم من قاعدة البيانات

    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.restaurant))  # هذا يقوم بعمل JOIN تلقائي
        .filter(Booking.user_id == user.id)
        .order_by(Booking.date.desc()) 
        .all()
    )

    # إعادة قائمة الحجوزات كـ JSON
    return {
        "status": "success",
        "data": [
            {

            "id": b.id,
            "restaurant_name": b.restaurant.name if b.restaurant else "غير معروف",
            "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"),
            "people": b.people,
            "status": b.status,
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        } for b in bookings]
    }


# عرض جميع الحجوزات - خاص بالأدمن فقط
@app.get("/api/admin/bookings")
def list_all_bookings_for_admin(db: Session = Depends(get_db), user: User = Depends(admin_required)):
    # فقط الأدمن يمكنه الوصول
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.restaurant), joinedload(Booking.user))
        .order_by(Booking.date.desc())
        .all()
    )

    # إعادة كل الحجوزات
    return {
        "status": "success",
        "data": [
            {
                "id": b.id,
                "user_name": b.user.fullname if b.user else "غير معروف",
                "restaurant_name": b.restaurant.name if b.restaurant else "غير معروف",
                "date": b.date.isoformat(),
                "time": b.time.strftime("%H:%M"),
                "people": b.people,
                "status": b.status,
                "created_at": b.created_at.isoformat(),
                "updated_at": b.updated_at.isoformat(),
            }
            for b in bookings
        ],
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



FastAPI
