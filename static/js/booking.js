// اختيار الفورم و div لعرض الرسائل
const bookingForm = document.getElementById('bookingForm');
const messageDiv = document.getElementById('message');

if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // منع إعادة تحميل الصفحة

        // جمع البيانات من الفورم والتأكد من النوع الصحيح
        const formData = {
            date: document.getElementById('date').value,         // تاريخ الحجز
            time: String(document.getElementById('time').value), // وقت الحجز كنص
            people: parseInt(document.getElementById('people').value, 10) // عدد الأشخاص كرقم
        };

        // التحقق من تعبئة كل الحقول
        if (!formData.date || !formData.time || isNaN(formData.people)) {
            messageDiv.style.display = 'block';
            messageDiv.className = 'message error';
            messageDiv.innerText = 'يرجى تعبئة جميع الحقول بشكل صحيح.';
            return;
        }

        try {
            const response = await fetch('/bookings', {
                method: 'POST',                   // ← فاصلة بعد كل سطر إلا الأخير
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
                credentials: 'include'          
            });

            const result = await response.json();
            messageDiv.style.display = 'block';

            if (response.ok) {
                messageDiv.className = 'message success';
                messageDiv.innerText = `تم تأكيد الحجز في ${result.date} الساعة ${result.time}`;
                bookingForm.reset();
            } else {
                messageDiv.className = 'message error';
                messageDiv.innerText = result.detail || 'حدث خطأ أثناء الحجز.';
            }
        } catch (error) {
            messageDiv.style.display = 'block';
            messageDiv.className = 'message error';
            messageDiv.innerText = 'حدث خطأ في الاتصال بالخادم.';
            console.error(error);
        }
    });
}
