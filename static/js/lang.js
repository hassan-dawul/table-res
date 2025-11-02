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
    changeLanguage(newLang); // تحديث النصوص والاتجاه
    // تحديث نص الزر نفسه

    location.reload()
};


    const lang = localStorage.getItem('site-lang') || 'ar'; // استرجاع اللغة أو العربية افتراضي
    changeLanguage(lang); // تطبيق النصوص
  

});
