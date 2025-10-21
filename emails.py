import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()  # يحمل القيم من .env

# إعدادات البريد (SMTP) من ملف .env
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

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

# إرسال إيميل ترحيبي للمستخدم الجديد
def send_welcome_email(user_name, user_email):
    subject = "مرحباً بك في موقعنا!"
    body = f"""مرحباً {user_name}،

شكراً لتسجيلك في موقعنا. حسابك تم إنشاؤه بنجاح.

نتمنى لك تجربة رائعة معنا!

مع تحيات فريقنا
"""
    send_email(user_email, subject, body)

# إرسال إيميل تأكيد الحجز
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
