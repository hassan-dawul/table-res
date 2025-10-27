import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()  # تحميل إعدادات البريد من .env

# إعدادات الخادم البريدي
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")


# دالة الإرسال العامة
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email} successfully!")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


# ✉️ إيميل ترحيبي
def send_welcome_email(user_name, user_email):
    subject = "مرحباً بك في موقعنا!"
    body = f"""مرحباً {user_name}،

شكراً لتسجيلك في موقعنا. حسابك تم إنشاؤه بنجاح.

نتمنى لك تجربة رائعة معنا!

مع تحيات فريقنا
"""
    send_email(user_email, subject, body)


# 📅 إيميل تأكيد الحجز
def send_booking_confirmation(user_name, user_email, booking_id, date, time, service_name):
    subject = "تأكيد حجزك"
    body = f"""مرحباً {user_name}،

شكراً لحجزك معنا. تفاصيل الحجز كالتالي:

رقم الحجز: {booking_id}
التاريخ: {date}
الوقت: {time}
الخدمة: {service_name}

نحن نتطلع لاستقبالك!

مع تحيات فريقنا
"""
    send_email(user_email, subject, body)


# ❌ إيميل إلغاء الحجز الجديد
# إرسال إيميل إلغاء الحجز
def send_booking_cancellation(user_name, user_email, booking_id, date, time, service_name):
    subject = "تم إلغاء حجزك"
    body = f"""مرحباً {user_name}،

تم إلغاء حجزك بنجاح. تفاصيل الحجز كانت كالتالي:

رقم الحجز: {booking_id}
التاريخ: {date}
الوقت: {time}
الخدمة: {service_name}

نأسف لأي إزعاج، ونتمنى أن نراك قريباً!

مع تحيات فريقنا
"""
    send_email(user_email, subject, body)
