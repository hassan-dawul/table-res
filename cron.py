# cron.py - Scheduler لتحديث الحجوزات المنتهية
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from db import get_db
from models import Booking, BookingStatus
import time

def cleanup_expired_bookings():
    """
    تغيّر حالة الحجوزات التي لم يتم دفعها بعد انتهاء المدة إلى Cancelled.
    """
    db = next(get_db())
    expiration = datetime.now() - timedelta(minutes=2)  # مدة انتهاء الحجز
    
    expired_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.pending,
        Booking.created_at < expiration
    ).all()

    for b in expired_bookings:
        b.status = BookingStatus.cancelled

    db.commit()
    print(f"[{datetime.now(timezone.utc)}] Updated {len(expired_bookings)} bookings to Cancelled")

# إعداد الـ scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_bookings, 'interval', minutes=1)  # كل  دقائق
scheduler.start()
print("Scheduler started...")

# إبقاء السكربت يعمل في الخلفية
while True:
    time.sleep(60)
