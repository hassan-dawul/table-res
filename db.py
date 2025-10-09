from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قراءة متغيرات قاعدة البيانات من البيئة
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS", "")  # كلمة السر، افتراضي فاضية
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# تكوين رابط الاتصال بقاعدة بيانات MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# إنشاء محرك الاتصال بقاعدة البيانات
engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4"},  # لضمان دعم الأحرف العربية والرموز
    echo=True  # لتفعيل طباعة الاستعلامات على الكونسول (debug)
)

# تعريف Base لإنشاء الجداول من خلال SQLAlchemy ORM
Base = declarative_base()

# إنشاء جلسة للتعامل مع قاعدة البيانات
SessionLocal = sessionmaker(
    autocommit=False,  # منع الحفظ التلقائي، تحتاج commit صريح
    autoflush=False,   # منع ال flush التلقائي قبل الاستعلامات
    bind=engine
)
