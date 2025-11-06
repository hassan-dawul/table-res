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
      "no-bookings": "لا توجد حجوزات حالياً.",
      "error-loading-bookings": "حدث خطأ في تحميل الحجوزات.",
      "cancel-confirm": "هل أنت متأكد من الإلغاء؟",
      "cancel-success": "✅ تم الإلغاء بنجاح",
      "cancel-failed": "⚠️ حدث خطأ أثناء الإلغاء",
      "logout-error": "⚠️ خطأ أثناء تسجيل الخروج",
      "cancel-btn": "إلغاء",
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
        "bookingSuccess": "✅ تم تأكيد الحجز بتاريخ {date} الساعة {time} لعدد {people} أشخاص.",
        "bookingError": "⚠️ حدث خطأ أثناء تنفيذ الحجز",
        "connectionError": "⚠️ خطأ في الاتصال بالخادم",
        "restaurantCapacityValue": "شخص",
        //contact
"contactTitle": "تواصل معنا",
"contactIntro": "إذا عندك سؤال أو اقتراح، اكتب لنا وسنرد بأقرب وقت.",
"labelName": "الاسم",
"labelEmail": "البريد الإلكتروني",
"labelSubject": "الموضوع",
"labelMessage": "الرسالة",
"sendBtn": "إرسال",
"successMsg": "✅ تم إرسال الرسالة بنجاح. سنرد عليك قريباً.",
"errorMsg": "حدث خطأ أثناء إرسال الرسالة. حاول لاحقاً.",
"invalidFields": "الرجاء تعبئة الحقول المطلوبة.",

  


    




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
      "no-bookings": "No bookings available.",
      "error-loading-bookings": "An error occurred while loading bookings.",
      "cancel-confirm": "Are you sure you want to cancel?",
      "cancel-success": "✅ Cancelled successfully",
      "cancel-failed": "⚠️ Error occurred while cancelling",
      "logout-error": "⚠️ Error during logout",
      "cancel-btn": "cancellation",
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
        "bookingSuccess": "✅ Booking confirmed on {date} at {time} for {people} people.",
        "bookingError": "⚠️ Error processing the booking",
        "connectionError": "⚠️ Connection error",
        "restaurantCapacityValue": "Capacity",
        //contact
"contactTitle": "Contact Us",
"contactIntro": "If you have a question or suggestion, send us a message and we'll reply soon.",
"labelName": "Name",
"labelEmail": "Email",
"labelSubject": "Subject",
"labelMessage": "Message",
"sendBtn": "Send",
"successMsg": "✅ Message sent successfully. We'll get back to you soon.",
"errorMsg": "An error occurred while sending. Please try again later.",
"invalidFields": "Please fill in the required fields.",






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
