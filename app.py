import os
import json

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESTAURANTS_FILE = os.path.join(DATA_DIR, "restaurants.json")

def ensure_data_files():
    # لو مجلد البيانات مش موجود، نسويه
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # لو users.json مش موجود، نخلقه بمصفوفة فارغة
    if not os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)  # يكتب [] في الملف
    
    # نفس الشيء لملف restaurants.json
    if not os.path.isfile(RESTAURANTS_FILE):
        with open(RESTAURANTS_FILE, "w") as f:
            json.dump([], f)
def read_json_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)  # تحول JSON لكائن بايثون

def write_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)  # تحول بيانات بايثون لـ JSON وتحفظ
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/ok")
async def ok():
    return JSONResponse(content={"status": "success", "message": "The API is working."})
