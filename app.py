from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
import bcrypt
import secrets
from datetime import datetime

# استيراد الاتصال بقاعدة البيانات والنماذج
from db import SessionLocal, engine, Base
from models import User, Restaurant

# إنشاء تطبيق FastAPI
app = FastAPI()

# عند بدء التشغيل، ننشّئ الجداول (إذا ما كانت موجودة)
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# دالة لمشاركة جلسة DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# نقطة اختبار
@app.get("/ok")
async def ok():
    return JSONResponse(content={"status": "success", "message": "The API is working."})

# استرجاع المطاعم مع الفلاتر
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
    # تحويل العناصر إلى dict عشان تقدر ترسل JSON
    return {"status": "success", "data": [ { "id": r.id, "name": r.name, "area": r.area, "cuisine": r.cuisine } for r in restaurants ]}

# تفاصيل مطعم معين
@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if restaurant:
        return {"status": "success", "data": { "id": restaurant.id, "name": restaurant.name, "area": restaurant.area, "cuisine": restaurant.cuisine }}
    raise HTTPException(status_code=404, detail="المطعم غير موجود")

# تسجيل مستخدم جديد
@app.post("/register", status_code=201)
async def register_user(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    if not all([fullname, email, password, password_confirmation]):
        return JSONResponse(status_code=400, content={"status": "error", "message": "جميع الحقول مطلوبة."})

    if password != password_confirmation:
        return JSONResponse(status_code=400, content={"status": "error", "message": "كلمتا المرور غير متطابقتين."})

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return JSONResponse(status_code=409, content={"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل."})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    token = secrets.token_hex(16)

    new_user = User(fullname=fullname, email=email, password=hashed_password, token=token)
    db.add(new_user)
    db.commit()

    return JSONResponse(status_code=201, content={
        "status": "ok",
        "fullname": fullname,
        "email": email,
        "token": token
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
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "message": "تم تسجيل الدخول بنجاح",
            "email": email,
            "token": token,
            "last_login": user.last_login.isoformat()
        })
    return JSONResponse(status_code=401, content={"status": "error", "message": "بيانات الدخول غير صحيحة"})

# عرض ملف المستخدم حسب التوكن
@app.get("/profile")
async def get_profile(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="الرمز غير موجود أو غير صالح.")
    token = authorization.replace("Bearer ", "").strip()
    user = db.query(User).filter(User.token == token).first()
    if user:
        return {
            "status": "success",
            "data": {
                "fullname": user.fullname,
                "email": user.email,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
    raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي.")
