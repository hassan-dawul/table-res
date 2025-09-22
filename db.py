from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# تعريف قاعدة البيانات
DATABASE_URL = "mysql+pymysql://root@localhost:3306/tabel"

# إنشاء الاتصال
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})

# تعريف Base
Base = declarative_base()

# إنشاء الجلسة
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
