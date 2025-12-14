$(document).ready(function() {

  // الترجمة عربي/انجليزي
  const translations = {
    ar: {
      "lang-ar": "English",
      // الصفحة الرئيسية
      "hero-title": "احجز طاولتك بسهولة — دليل موحّد لمطاعم مدينتك",
      "hero-desc": "منصّة تعريفية تجمع أفضل المطاعم وتبسّط طريقك للحجز عبر شركائنا. استكشف حسب المدينة والمطبخ والميزانية.",
      "explore-btn": "استكشف المطاعم",
      "about-section-title": "من نحن؟",
      "about-title": "نحن منصة تهدف لتسهيل عملية اكتشاف وحجز المطاعم",
      "about-desc": "نوفر لك تجربة سلسة لاستكشاف المطاعم المناسبة لك، مع إمكانية الحجز الفوري.",
      "book-now-btn": "احجز الآن",
      "feature1-title": "واجهة سهلة",
      "feature1-desc": "صممنا منصتنا بواجهة استخدام بسيطة وسهلة، لتمنحك تجربة مريحة وسريعة.",
      "feature2-title": "معلومات دقيقة",
      "feature2-desc": "نوفر لك معلومات دقيقة ومحدثة عن كل مطعم، تشمل قائمة الطعام، الأسعار، ساعات العمل، والموقع.",
      "feature3-title": "شراكات",
      "feature3-desc": "شراكاتنا مع أكثر من 2000 مطعم تتيح لنا عرض معلومات دقيقة وتأكيد الحجوزات بشكل فوري.",
      "how-it-works-title": "كيف تعمل الخدمة؟",
      "step1-title": "استكشف",
      "step1-desc": "استكشف أفضل المطاعم حولك بكل سهولة، مع تفاصيل دقيقة تساعدك على اتخاذ القرار الصحيح.",
      "step2-title": "اختر",
      "step2-desc": "اختر المطعم الذي يناسب ذوقك واحتياجاتك من بين مئات الخيارات المصنفة والموثوقة.",
      "step3-title": "احجز عبر شريك",
      "step3-desc": "احجز طاولتك مباشرة عبر شريكنا بكل سرعة وأمان، واستمتع بتجربة خالية من التعقيد.",
      "restaurants-title": "المطاعم المتاحة",
      "more-restaurants-btn": "المزيد من المطاعم",
      "tags-title": "تعرّف على خياراتك",
      "tag-riyadh": "الرياض",
      "tag-jeddah": "جدة",
      "tag-dammam": "الدمام",
      "tag-italian": "إيطالي",
      "tag-indian": "هندي",
      "tag-arabic": "شرقي",
      "cta-title": "جاهز لاكتشاف مطعمك القادم؟",
      "contact-btn": "تواصل معنا",

      // صفحة البروفايل
      "profile-welcome": "مرحبا بك،",
      "profile-email": "البريد الإلكتروني:",
      "profile-last-login": "آخر تسجيل دخول:",
      "profile-logout": "تسجيل الخروج",
      "bookings-title": "حجوزاتي القادمة:",
      "table-id": "#",
      "table-restaurant": "المطعم",
      "table-date": "التاريخ",
      "table-time": "الوقت",
      "table-people": "عدد الأشخاص",
      "table-status": "الحالة",
      "table-actions": "إجراءات",
      "status-confirmed": "مؤكد",
      "status-cancelled": "ملغي",
      "status-pending": "قيد الانتظار",
      "no-bookings": "لا توجد حجوزات حالياً.",
      "error-loading-bookings": "حدث خطأ في تحميل الحجوزات.",
      "cancel-confirm": "هل أنت متأكد من الإلغاء؟",
      "cancel-success": "✅ تم الإلغاء بنجاح",
      "cancel-failed": "⚠️ حدث خطأ أثناء الإلغاء",
      "logout-error": "⚠️ خطأ أثناء تسجيل الخروج",
      "cancel-btn": "إلغاء",
      "pay-btn": "ادفع الآن",

          // HEADER
    "nav-bookings": "الحجوزات",
    "nav-home": "الرئيسية",
    "nav-about": "عنّا",
    "nav-how": "كيف نعمل",
    "nav-contact": "تواصل",
    "btn-profile": "الملف الشخصي",
    "btn-logout": "تسجيل الخروج",
    "btn-login": "تسجيل الدخول",
    "btn-register": "اشتراك",
        //مطاعم 
      "location": "الموقع",
      "hours": "ساعات العمل",
      "capacity": "السعة",
      "bookNow": "احجز الآن",
      "cuisineType": "نوع المطبخ",
      
      "filters": "الفلاتر",
      "searchPlaceholder": "ابحث عن مطعم...",
      "search-btn": "بحث",
      "area": "المنطقة",
      "all": "الكل",
      "workingHours": "ساعات العمل",
      "capacity": "السعة",
      "bookNow": "احجز الآن",
      "guests": "ضيف",
      "errorFetch": "حدث خطأ في جلب بيانات المطاعم.",
              "errorFetchMsg": "حدث خطأ في جلب بيانات المطاعم.",
        "noRestaurantsMsg": "لا توجد مطاعم مطابقة للبحث.",
        "todayBookingsLabel": "عدد الحجز اليوم",


      // register
    "register-title": "إنشاء حساب جديد",
    "label-fullname": "اسم المستخدم",
    "label-email": "البريد الإلكتروني",
    "label-password": "كلمة المرور",
    "password-hint": "يجب أن تتراوح كلمة المرور بين 8 و20 حرفًا وتحتوي على حروف وأرقام فقط.",
    "label-confirm": "تأكيد كلمة المرور",
    "register-btn": "تسجيل",
    "already-have": "لديك حساب؟",
    "login-link": "تسجيل الدخول",
        // login
    "login_title": "تسجيل الدخول",
    "password_label": "كلمة المرور",
    "login_btn": "تسجيل الدخول",
    "no_account_text": "ليس لديك حساب؟",
    "register_link": "إنشاء حساب جديد",
    "footer-text": "حقوق الطبع والنشر © 2025 - طاولتك",
    //booking
        "bookingTitle": "حجز طاولة",
        "bookingSectionTitle": "حجز طاولة",
        "dateLabel": "التاريخ:",
        "timeLabel": "الوقت:",
        "timePlaceholder": "اختر الساعة",
        "peopleLabel": "عدد الأشخاص:",
        "submitBtn": "احجز الآن",
        "loadingRestaurant": "جاري تحميل بيانات المطعم...",
        "restaurantNameLabel": "اسم المطعم",
        "restaurantCuisineLabel": "نوع المطبخ",
        "restaurantAreaLabel": "المنطقة",
        "restaurantHoursLabel": "ساعات العمل",
        "restaurantCapacityLabel": "السعة",
        "restaurantNotFound": "المطعم غير موجود",
        "restaurantLoadError": "حدث خطأ أثناء تحميل بيانات المطعم",
        "bookingSuccess": "✅ جاري تحويلك إلى صفحة الدفع...",
        "bookingError": "⚠️ حدث خطأ أثناء تنفيذ الحجز",
        "connectionError": "⚠️ خطأ في الاتصال بالخادم",
        "restaurantCapacityValue": "شخص",
        "restaurantCapacityValue": "السعة",
"availabilityRemaining": "متبقي <strong>{remaining}</strong> أماكن للحجز",
"availabilityFull": "لا توجد أماكن متاحة في هذا الوقت",
"availabilityCheckError": "⚠️ خطأ أثناء التحقق من التوفر",
"availabilityConnectionError": "⚠️ خطأ في الاتصال بالخادم",

        //contact
    "contact-title": "تواصل معنا",
    "contact-intro": "إذا عندك سؤال أو اقتراح، اكتب لنا وسنرد بأقرب وقت.",
    "label-name": "الاسم",
    "label-email": "البريد الإلكتروني",
    "label-subject": "الموضوع",
    "label-message": "الرسالة",
    "send-btn": "إرسال",
    "success-msg": "✅ تم إرسال الرسالة بنجاح. سنرد عليك قريباً.",
    "error-msg": "حدث خطأ أثناء إرسال الرسالة. حاول لاحقاً.",
    "invalid-fields": "الرجاء تعبئة الحقول المطلوبة.",
        "namePlaceholder": "الاسم",
    "subjectPlaceholder": "موضوع الرسالة",
    "messagePlaceholder": "اكتب رسالتك هنا...",
       //booking-success
    "payment-success-title": "✅ تم الدفع بنجاح",
    "payment-success-subtitle": "شكراً لك على حجز طاولتك.",
    "invoice-title": "فاتورة الحجز",
    "loading-text": "جارٍ تحميل بيانات الحجز...",
    "profile-btn": "العودة للملف الشخصي",
    "new-booking-btn": "حجز جديد",
           "user-name": "اسم المستخدم:",
        "user-email": "البريد الإلكتروني:",
        "restaurant-name": "المطعم:",
        "booking-date": "التاريخ:",
        "booking-time": "الوقت:",
        "booking-people": "عدد الأشخاص:",
        "amount-paid": "المبلغ المدفوع:",
        "loading": "جارٍ تحميل بيانات الحجز...",
        "no-booking": "لا توجد بيانات للحجز.",
        "error-loading": "فشل تحميل بيانات الحجز.",
        "cannot-define": "لا يمكن تحديد الحجز.",
        "currency": "ريال",
        "payment-title": "إتمام الدفع",
        "payment-subtitle": "سيتم معالجة الدفع بشكل آمن لإتمام حجزك.",


        // عنّا
        "about-title": "عنّا",
        "about-title-h2": "عنّا",
        "about-card-1-title": "سرعة وفعالية",
        "about-text-1": "نحن منصة متخصصة في تسهيل حجز الطاولات في المطاعم المفضلة لديك بطريقة سريعة وآمنة.",
        "about-card-2-title": "تجربة المستخدم",
        "about-text-2": "هدفنا هو توفير تجربة سلسة للمستخدمين مع أفضل المطاعم وخدمة عملاء ممتازة.",
        "about-card-3-title": "أهمية الوقت",
        "about-text-3": "نؤمن بأهمية الوقت وتجربة المستخدم لذلك صممنا نظامنا ليكون بسيط وفعال.",
        "about-card-4-title": "تحديث مستمر",
        "about-text-4": "نعمل على تحديث خدماتنا باستمرار لتلبية احتياجات جميع عملائنا.",

        // كيف نعمل
        "how-title": "كيف نعمل",
        "how-title-h2": "كيف نعمل",
        "how-step-1-title": "اختيار المطعم",
        "how-step-1-text": "اختر مطعمك المفضل من قائمة المطاعم المتوفرة.",
        "how-step-2-title": "حجز الطاولة",
        "how-step-2-text": "قم بحجز الطاولة المناسبة حسب التاريخ والوقت.",
        "how-step-3-title": "الدفع والاستمتاع",
        "how-step-3-text": "أتمم الدفع واستمتع بتجربة رائعة في المطعم.",
        "how-step-4-title": "خدمة متميزة",
        "how-step-4-text": "نضمن لك تجربة ممتازة وخدمة عملاء سريعة وفعالة.",
      "pagination-prev": "السابق",
    "pagination-next": "التالي",
        //chat
    "nav-chat": "الشات",
   
"chat-title": "الشات",
        "ask-restaurant": "اسأل عن مطعم...",
        "send-btn": "إرسال",
        "user-prefix": "أنت",
        "bot-error": "بوت: حدث خطأ، حاول مرة أخرى",
        "open-now": "مفتوح الآن",
        "closed-now": "مغلق الآن",
        "capacity-info": "السعة: {capacity} ضيوف",
        "most-booked": "الأكثر حجزًا اليوم",
        "book-now-btn": "احجز الآن",











  


    




    },

    en: {
      "lang-ar": "عربي",
      // الصفحة الرئيسية
      "hero-title": "Book your table easily — Your city's restaurant guide",
      "hero-desc": "A platform that brings the best restaurants and simplifies booking through our partners. Explore by city, cuisine, and budget.",
      "explore-btn": "Explore Restaurants",
      "about-section-title": "About Us",
      "about-title": "We are a platform that simplifies discovering and booking restaurants",
      "about-desc": "We provide a seamless experience to find the right restaurants, with instant booking.",
      "book-now-btn": "Book Now",
      "feature1-title": "Easy Interface",
      "feature1-desc": "We designed our platform with a simple and user-friendly interface for a smooth experience.",
      "feature2-title": "Accurate Info",
      "feature2-desc": "We provide accurate and updated info about each restaurant including menu, prices, hours, and location.",
      "feature3-title": "Partnerships",
      "feature3-desc": "Our partnerships with over 2000 restaurants allow instant booking confirmations.",
      "how-it-works-title": "How It Works",
      "step1-title": "Explore",
      "step1-desc": "Explore the best restaurants around you easily, with detailed info to make the right decision.",
      "step2-title": "Choose",
      "step2-desc": "Choose the restaurant that fits your taste and needs from hundreds of verified options.",
      "step3-title": "Book via Partner",
      "step3-desc": "Book your table directly through our partner quickly and safely.",
      "restaurants-title": "Available Restaurants",
      "more-restaurants-btn": "More Restaurants",
      "tags-title": "Discover your options",
      "tag-riyadh": "Riyadh",
      "tag-jeddah": "Jeddah",
      "tag-dammam": "Dammam",
      "tag-italian": "Italian",
      "tag-indian": "Indian",
      "tag-arabic": "Arabic",
      "cta-title": "Ready to discover your next restaurant?",
      "contact-btn": "Contact Us",

      // صفحة البروفايل
      "profile-welcome": "Welcome,",
      "profile-email": "Email:",
      "profile-last-login": "Last login:",
      "profile-logout": "Logout",
      "bookings-title": "My Upcoming Bookings:",
      "table-id": "#",
      "table-restaurant": "Restaurant",
      "table-date": "Date",
      "table-time": "Time",
      "table-people": "Guests",
      "table-status": "Status",
      "table-actions": "Actions",
      "status-confirmed": "Confirmed",
      "status-cancelled": "Cancelled",
      "status-pending": "pending",
      "no-bookings": "No bookings available.",
      "error-loading-bookings": "An error occurred while loading bookings.",
      "cancel-confirm": "Are you sure you want to cancel?",
      "cancel-success": "✅ Cancelled successfully",
      "cancel-failed": "⚠️ Error occurred while cancelling",
      "logout-error": "⚠️ Error during logout",
      "cancel-btn": "cancellation",
      "pay-btn": "Pay Now",

          // HEADER
    "nav-bookings": "Bookings",
    "nav-home": "Home",
    "nav-about": "About",
    "nav-how": "How It Works",
    "nav-contact": "Contact",
    "btn-profile": "Profile",
    "btn-logout": "Logout",
    "btn-login": "Login",
    "btn-register": "Register",
       //مطاعم
      "location": "Location",
      "hours": "Working Hours",
      "capacity": "Capacity",
      "bookNow": "Book Now",

      "filters": "Filters",
      "searchPlaceholder": "Search for a restaurant...",
      "search-btn": "Search",
      "cuisineType": "Cuisine Type",
      "area": "Area",
      "all": "All",
      
      "workingHours": "Working Hours",
      "capacity": "Capacity",
      "bookNow": "Book Now",
      "guests": "Guests",
      "errorFetch": "Error fetching restaurant data.", 
              "errorFetchMsg": "Failed to fetch restaurant data.",
        "noRestaurantsMsg": "No restaurants match your search.",
        "todayBookingsLabel": "Bookings Today",
  

      // register
    "register-title": "Create a New Account",
    "label-fullname": "Username",
    "label-email": "Email Address",
    "label-password": "Password",
    "password-hint": "Password must be 8–20 characters long and contain letters and numbers only.",
    "label-confirm": "Confirm Password",
    "register-btn": "Sign Up",
    "already-have": "Already have an account?",
    "login-link": "Login",

    // login
    "login_title": "Login",
    "email_label": "Email",
    "password_label": "Password",
    "login_btn": "Sign In",
    "no_account_text": "Don’t have an account?",
    "register_link": "Create new account",
    //booking
    "footer-text": "Copyright © 2025 - Tawletk",
        "bookingTitle": "Table Booking",
        "bookingSectionTitle": "Table Booking",
        "dateLabel": "Date:",
        "timeLabel": "Time:",
        "timePlaceholder": "Select time",
        "peopleLabel": "Number of people:",
        "submitBtn": "Book Now",
        "loadingRestaurant": "Loading restaurant data...",
        "restaurantNameLabel": "Restaurant Name",
        "restaurantCuisineLabel": "Cuisine Type",
        "restaurantAreaLabel": "Area",
        "restaurantHoursLabel": "Working Hours",
        "restaurantCapacityLabel": "Capacity",
        "restaurantNotFound": "Restaurant not found",
        "restaurantLoadError": "Error loading restaurant data",
        "bookingSuccess": "✅ Redirecting you to the payment page...",
        "bookingError": "⚠️ Error processing the booking",
        "connectionError": "⚠️ Connection error",
        "restaurantCapacityValue": "Capacity",
        "availabilityRemaining": "Remaining <strong>{remaining}</strong> seats available",
"availabilityFull": "No seats available at this time",
"availabilityCheckError": "⚠️ Error checking availability",
"availabilityConnectionError": "⚠️ Server connection error",


        
        //contact
    "contact-title": "Contact Us",
    "contact-intro": "If you have any question or suggestion, write to us and we will reply as soon as possible.",
    "label-name": "Name",
    "label-email": "Email",
    "label-subject": "Subject",
    "label-message": "Message",
    "send-btn": "Send",
    "success-msg": "✅ Message sent successfully. We will reply soon.",
    "error-msg": "Error sending the message. Please try again later.",
    "invalid-fields": "Please fill in all required fields.",
        "namePlaceholder": "Name",
    "subjectPlaceholder": "Subject of the message",
    "messagePlaceholder": "Write your message here...",
    //booking-success
    "payment-success-title": "✅ Payment Successful",
    "payment-success-subtitle": "Thank you for booking your table.",
    "invoice-title": "Booking Invoice",
    "loading-text": "Loading booking details...",
    "profile-btn": "Back to Profile",
    "new-booking-btn": "New Booking",
            "user-name": "User Name:",
        "user-email": "Email:",
        "restaurant-name": "Restaurant:",
        "booking-date": "Date:",
        "booking-time": "Time:",
        "booking-people": "Number of People:",
        "amount-paid": "Amount Paid:",
        "loading": "Loading booking details...",
        "no-booking": "No booking data.",
        "error-loading": "Failed to load booking details.",
        "cannot-define": "Cannot determine booking.",
        "currency": "SAR",
        "payment-title": "Complete Payment",
        "payment-subtitle": "Your booking will be securely processed.",

        // About Us
        "about-title": "About Us",
        "about-title-h2": "About Us",
        "about-card-1-title": "Speed & Efficiency",
        "about-text-1": "We are a platform specialized in making table reservations at your favorite restaurants fast and secure.",
        "about-card-2-title": "User Experience",
        "about-text-2": "Our goal is to provide a seamless experience for users with the best restaurants and excellent customer service.",
        "about-card-3-title": "Time Matters",
        "about-text-3": "We value time and user experience, so we designed our system to be simple and efficient.",
        "about-card-4-title": "Continuous Update",
        "about-text-4": "We continuously update our services to meet the needs of all our customers.",

        // How We Work
        "how-title": "How We Work",
        "how-title-h2": "How We Work",
        "how-step-1-title": "Choose Restaurant",
        "how-step-1-text": "Select your favorite restaurant from our available list.",
        "how-step-2-title": "Reserve Table",
        "how-step-2-text": "Book a table according to your preferred date and time.",
        "how-step-3-title": "Pay & Enjoy",
        "how-step-3-text": "Complete payment and enjoy a great experience at the restaurant.",
        "how-step-4-title": "Excellent Service",
        "how-step-4-text": "We guarantee an excellent experience and fast, efficient customer service.",
        "pagination-prev": "Previous",
    "pagination-next": "Next",
          //chat
    "nav-chat": "Chat",
        "chat-title": "Chat",
        "ask-restaurant": "Ask about a restaurant...",
        "send-btn": "Send",
        "user-prefix": "You",
        "bot-error": "Bot: An error occurred, try again",
        "open-now": "Open now",
        "closed-now": "Closed now",
        "capacity-info": "Capacity: {capacity} guests",
        "most-booked": "Most booked today",
        "book-now-btn": "Book Now",




    










    }
  };

  // 🔹 2️⃣ دالة لتحديث النصوص في الصفحة حسب اللغة
  function updateTexts(lang) {
    const data = translations[lang];
    Object.keys(data).forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = data[id]; // تحديث النص
    });

    // 🔹 2a️⃣ تغيير اتجاه الصفحة (RTL/ LTR)
    document.documentElement.style.setProperty('--page-dir', lang === 'ar' ? 'rtl' : 'ltr');

  }

  // 🔹 3️⃣ تحميل اللغة المحفوظة سابقًا أو الافتراضية عند تحميل الصفحة
  document.addEventListener('DOMContentLoaded', () => {
    const lang = localStorage.getItem('site-lang') || 'ar'; // استرجاع اللغة من localStorage
    updateTexts(lang); // تطبيق اللغة
  });

  // 🔹 4️⃣ دالة لتغيير اللغة وحفظها لاستخدامها في الصفحات القادمة
  window.changeLanguage = function(lang) {
    updateTexts(lang); // تغيير النصوص
    localStorage.setItem('site-lang', lang); // حفظ اللغة في localStorage
    // 
  };

// زر واحد لتبديل اللغة
const langToggle = document.getElementById('lang-ar'); // استخدم الزر الموجود
langToggle.onclick = () => {
    const currentLang = localStorage.getItem('site-lang') || 'ar';
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    localStorage.setItem('site-lang', newLang);
    // تحديث نص الزر نفسه

    location.reload()
};


    const lang = localStorage.getItem('site-lang') || 'ar'; // استرجاع اللغة أو العربية افتراضي
    changeLanguage(lang); // تطبيق النصوص


});
