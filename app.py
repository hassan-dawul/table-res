import os
import json
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESTAURANTS_FILE = os.path.join(DATA_DIR, "restaurants.json")

# وظيفة تتأكد من وجود مجلد البيانات والملفات المطلوبة
def ensure_data_files():
    # إذا مجلد البيانات غير موجود، يتم إنشاؤه
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # إذا ملف المستخدمين غير موجود، يتم إنشاؤه كمصفوفة فاضية
    if not os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    
    # نفس الشيء لملف المطاعم
    if not os.path.isfile(RESTAURANTS_FILE):
        with open(RESTAURANTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

# قراءة البيانات من ملف JSON وتحويلها لكائن بايثون
def read_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# كتابة بيانات بايثون إلى ملف JSON
def write_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# إنشاء التطبيق
app = FastAPI()

# عند بدء التشغيل، تأكد من وجود الملفات
@app.on_event("startup")
def startup_event():
    ensure_data_files()

# نقطة اختبار للتأكد أن الـ API تعمل
@app.get("/ok")
async def ok():
    return JSONResponse(content={"status": "success", "message": "The API is working."})

# المهمة 1 — قائمة المطاعم مع دعم الفلاتر (المنطقة والمطبخ)
@app.get("/restaurants")
def get_restaurants(area: Optional[str] = Query(None), cuisine: Optional[str] = Query(None)):
    restaurants = read_json_file(RESTAURANTS_FILE)

    if area:
        restaurants = [r for r in restaurants if r.get("area") == area]
    if cuisine:
        restaurants = [r for r in restaurants if r.get("cuisine") == cuisine]

    return {
        "status": "success",
        "data": restaurants
    }

# المهمة 2 — تفاصيل مطعم حسب الـ ID
@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int):
    restaurants = read_json_file(RESTAURANTS_FILE)

    for restaurant in restaurants:
        if restaurant.get("id") == restaurant_id:
            return {
                "status": "success",
                "data": restaurant
            }

    raise HTTPException(status_code=404, detail="المطعم غير موجود")

# المهمة 3 — تسجيل مستخدم جديد
@app.post("/register", status_code=201)
async def register_user(request: Request):
    data = await request.json()

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    # التأكد من وجود جميع الحقول وعدم كونها فارغة
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

    # التأكد من أن البريد الإلكتروني غير مستخدم سابقاً
    if any(user["email"] == email for user in users):
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل."}
        )

    # إضافة المستخدم الجديد
    new_user = {
        "fullname": fullname,
        "email": email,
        "password": password  # تنبيه: في المشاريع الفعلية يجب تشفير كلمة المرور
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

# المهمة 4 — تسجيل الدخول
@app.post("/login")
async def login_user(request: Request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")

    # التأكد من أن البريد وكلمة المرور موجودين
    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "البريد الإلكتروني وكلمة المرور مطلوبة."}
        )

    users = read_json_file(USERS_FILE)

    # البحث عن مستخدم يطابق البيانات
    user = next((u for u in users if u["email"] == email and u["password"] == password), None)

    if user:
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

# المهمة 5 — عرض ملف المستخدم عن طريق البريد الإلكتروني
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
