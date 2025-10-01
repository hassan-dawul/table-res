from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قراءة المتغيرات
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS", "")  # كلمة السر، افتراضي فاضية
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# تكوين رابط الاتصال بقاعدة بيانات MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# إنشاء الاتصال
engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4"},
    echo=True
)

# تعريف Base لإنشاء الجداول
Base = declarative_base()

# إنشاء الجلسة
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
