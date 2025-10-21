// حدد النموذج وصندوق الرسائل
const bookingForm = document.getElementById('bookingForm');
const messageDiv = document.getElementById('message');

// حدث عند إرسال النموذج
bookingForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // يمنع إعادة تحميل الصفحة

    // جمع البيانات من النموذج
    const bookingData = {
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        people: parseInt(document.getElementById('people').value)
    };

    try {
        // إرسال بيانات الحجز للـ API
        const response = await fetch('/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingData)
        });

        const result = await response.json();

        if (response.ok) {
            // عرض رسالة نجاح
            messageDiv.style.display = 'block';
            messageDiv.className = 'message success';
            messageDiv.textContent = `تم تأكيد حجزك بتاريخ ${bookingData.date} الساعة ${bookingData.time} لـ ${bookingData.people} أشخاص.`;
            bookingForm.reset(); // تفريغ النموذج بعد النجاح
        } else {
            // عرض رسالة خطأ
            messageDiv.style.display = 'block';
            messageDiv.className = 'message error';
            messageDiv.textContent = result.detail || 'حدث خطأ أثناء الحجز.';
        }

    } catch (error) {
        // خطأ بالشبكة أو السيرفر
        messageDiv.style.display = 'block';
        messageDiv.className = 'message error';
        messageDiv.textContent = 'فشل الاتصال بالخادم. حاول مرة أخرى.';
        console.error(error);
    }
});
