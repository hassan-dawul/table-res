from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# غير معلومات الاتصال حسب إعدادات MySQL عندك
DATABASE_URL = "mysql+pymysql://root@localhost:3306/tabel"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

