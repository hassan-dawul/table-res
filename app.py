import os
import json
import bcrypt  # 🔒 جديد: استيراد مكتبة التشفير
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESTAURANTS_FILE = os.path.join(DATA_DIR, "restaurants.json")

# إنشاء المجلد والملفات في حال عدم وجودها
def ensure_data_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    if not os.path.isfile(RESTAURANTS_FILE):
        with open(RESTAURANTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

# قراءة وكتابة JSON
def read_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# تهيئة التطبيق
app = FastAPI()

# التأكد من وجود الملفات عند التشغيل
@app.on_event("startup")
def startup_event():
    ensure_data_files()

# نقطة اختبار للتأكد أن الـ API تعمل
@app.get("/ok")
async def ok():
    return JSONResponse(content={"status": "success", "message": "The API is working."})

# استرجاع قائمة المطاعم مع فلاتر اختيارية
@app.get("/restaurants")
def get_restaurants(area: Optional[str] = Query(None), cuisine: Optional[str] = Query(None)):
    restaurants = read_json_file(RESTAURANTS_FILE)
    if area:
        restaurants = [r for r in restaurants if r.get("area") == area]
    if cuisine:
        restaurants = [r for r in restaurants if r.get("cuisine") == cuisine]
    return {"status": "success", "data": restaurants}

# تفاصيل مطعم معين
@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int):
    restaurants = read_json_file(RESTAURANTS_FILE)
    for restaurant in restaurants:
        if restaurant.get("id") == restaurant_id:
            return {"status": "success", "data": restaurant}
    raise HTTPException(status_code=404, detail="المطعم غير موجود")

# ✅ تسجيل مستخدم جديد مع تشفير كلمة المرور
@app.post("/register", status_code=201)
async def register_user(request: Request):
    data = await request.json()

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    # التحقق من أن جميع الحقول موجودة
    if not all([fullname, email, password, password_confirmation]):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "جميع الحقول مطلوبة."}
        )

    # التأكد من تطابق كلمتي المرور
    if password != password_confirmation:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "كلمتا المرور غير متطابقتين."}
        )

    users = read_json_file(USERS_FILE)

    # التحقق من أن البريد غير مستخدم مسبقًا
    if any(user["email"] == email for user in users):
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل."}
        )

    # 🔒 جديد: تشفير كلمة المرور قبل الحفظ
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # 🔒 جديد

    new_user = {
        "fullname": fullname,
        "email": email,
        "password": hashed_password  # 🔒 جديد: حفظ الكلمة بشكل مشفّر
    }
    users.append(new_user)
    write_json_file(USERS_FILE, users)

    return JSONResponse(
        status_code=201,
        content={
            "status": "ok",
            "fullname": fullname,
            "email": email
        }
    )

# ✅ تسجيل الدخول مع مقارنة كلمة المرور المشفرة
@app.post("/login")
async def login_user(request: Request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "البريد الإلكتروني وكلمة المرور مطلوبة."}
        )

    users = read_json_file(USERS_FILE)

    # 🔒 جديد: البحث عن المستخدم بالبريد فقط
    user = next((u for u in users if u["email"] == email), None)  # 🔒 جديد

    # 🔒 جديد: التحقق من مطابقة كلمة المرور المشفّرة
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):  # 🔒 جديد
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": "تم تسجيل الدخول بنجاح",
                "email": email
            }
        )
    else:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "بيانات الدخول غير صحيحة"
            }
        )

# عرض ملف المستخدم حسب البريد
@app.get("/profile")
async def get_profile(email: str):
    users = read_json_file(USERS_FILE)
    user = next((u for u in users if u["email"] == email), None)
    if user:
        return {
            "status": "success",
            "data": {
                "fullname": user["fullname"],
                "email": user["email"]
            }
        }
    else:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
