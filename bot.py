import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import re
import json
from datetime import datetime

BOT_TOKEN = "8773180444:AAFqH82a0WHIm6U2RG4knBUG1W2vBvJnSTI"

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# ========== بيانات Service Account مباشرة ==========
SERVICE_ACCOUNT_JSON = '''
{
  "type": "service_account",
  "project_id": "omaah-e3c65",
  "private_key_id": "e15e4c726fe52e2cfbd6d0b27d0ac5a6c8e6a10d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCrQpBzJ2CrkoCO\nyCId/MJ/s8AjMK7pdU82pKd+HGPDUbJv2AvLdOmiwiLsqte1qAeI/dLNiqTmGBfU\nFqCnCq3eAS+OQ/sWXHbu9zrer6au3W48e4O76Ehl5r6VfVSMqAH7I14CxIFUWS40\nPFZiyDR6OeT8FYuJJs2bqhorM2nV7bZQ8mIJnhD6Zgd5fwK9leAHFdlmEy3J593d\nUjV7WPQn42K30EK7R6+WUD2zTwlnlwrQkhw2Bkrm6mFkS2ZSO0po+CpqHfHkQ5Yf\ntvj1iPJ4Iu31iuggam02GjTik6E5KwSGGDvViyfVM/a//dIgqiKI7AoS7BEYSDHt\n+oKT7p7nAgMBAAECggEAEPFcgEGMpMZK0m7zDeufNyo9sr2MPSun37+mYMMtc3m2\nB3tkn1PWEVrXdBNRLkPzV7AuYyGspdhx8wxSB6fDNhiaVdH2TNE7ZIswJC7u2vnf\ngAhQKttHqx0kc0s05CPZUYXym2xJYMjgQB0ZoFtiJbCe+l/Y41BKPKfPDI5HkcXx\niqWNVX/WqPlkjXbCArhNySQ9bS/jN4idmx978DfgY9EKZmBOJJID2EbAN32MYu3C\nKnyFXPyJ7fPpMQCVyqnmK3vPiUodMcqKLKEAEJV6frH2bPQswC/5i1XuS9G1M+S/\nhDnUq+VR7sG7dV493S+Lb5OMP6yTPgKUSb30oPfisQKBgQDfcMRs1xUkeJ6OcgIq\nNR7cGFf7NAH0q6NIrtJsI/nWHCPsLwb9E6K9lo0088GN1V27nxPsRyRmmwOTItu7\ngkub+247sxnj9FRibE18Vybj0tRdyYwLtJ2HSAim2+XWq8p7MZWtl9J04xeP37bY\nUgOi7dGiGDI3YAN4M941yMJTswKBgQDEN0EdxvsbISKvKvS5lQ5MitRqKod4aR7u\n1kOeNGVU9Pbb16HQkr428V22xPqrXB/u26CHVs8Lmnc5tiD7uK8xwtNVOE0QvIlR\ndRdVClHDTY4KiWxSr47rIzQYJt3Dghoy5nAa0NcPruwIdx5un8xMwNfDgMQgqGMV\nwozxFy79/QKBgBb2UMlapSqVVr4Oy1gpE13NBqWjJ5xMU0Bx7t/8Jn2xcKOiBZbW\ngL/5C9PoRPjdd3+DjpmWihAdWBWz3F79ueVyxlZORpfdkRp4RNJFZpK9JOPqhYDi\nc9nmNjVnncwc5XcZlmc7lf47JD294N2EOClzRTriP67fKBwfQHPIiOfvAoGALaxK\n7Pp/Qt5gq3ONSZGHpYt/TEMgC4g0mhWn4bCCkdb/i0bTNLCjtDhUvxF04+Rqznez\nEy3CvgmzjOx3GwDvTt7xwFl9ntK0CBEAYFwpkhOAZ7V7UHfrBZLJMoIBhtvG62g2\nWheYp97otEO+ArQRoyAUWT6k6JEpl0wU8J2b46UCgYAgg4/2Y79LG2Yg4dlcsj8r\nE4c5T9Te97GfW1/QZcJ6rQ9Ln7h9dJL81tWNJmUI4xkwMHJaL+DuOl+WecYBsWPf\nuv+ZfROhpPgaillWBTLP0axRszbxwi4j11EXhrgsn+fPBgzkeNZZ2xssrIIUfSXv\nRTjAx5GVgqtTEyczwykQ2g==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@omaah-e3c65.iam.gserviceaccount.com",
  "client_id": "106554834168178241043",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40omaah-e3c65.iam.gserviceaccount.com"
}
'''

# ========== الاتصال بـ Firebase ==========
try:
    # تنظيف النص من أي مشاكل
    service_account_dict = json.loads(SERVICE_ACCOUNT_JSON)
    cred = credentials.Certificate(service_account_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully")
    print(f"📁 Project: {service_account_dict.get('project_id')}")
except Exception as e:
    print(f"❌ Firebase error: {e}")
    db = None

# ========== دوال البحث ==========
def normalize_text(text):
    """تطبيع النص للبحث (إزالة التشكيل والمسافات الزائدة)"""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # إزالة المسافات الزائدة
    text = text.replace('آ', 'ا').replace('إ', 'ا').replace('أ', 'ا')  # توحيد الألف
    text = text.replace('ى', 'ي').replace('ة', 'ه')  # توحيد الياء والتاء
    text = text.replace('ؤ', 'و').replace('ئ', 'ي')  # توحيد الواو والياء
    return text.lower()

def search_student(name):
    """البحث عن الطالب في قاعدة البيانات"""
    if db is None:
        print("❌ Database not connected")
        return None
    
    try:
        students_ref = db.collection('students')
        docs = students_ref.get()
        
        normalized_search = normalize_text(name)
        print(f"🔍 Searching for: '{normalized_search}'")
        
        # قائمة لتخزين النتائج المتعددة
        matches = []
        
        for doc in docs:
            student = doc.to_dict()
            student_name = student.get('name', '')
            student_code = student.get('code', '')
            student_level = student.get('overallLevel', 'غير محدد')
            
            normalized_name = normalize_text(student_name)
            
            # 1. تطابق تام
            if normalized_name == normalized_search:
                print(f"✅ Exact match: {student_name}")
                return student
            
            # 2. اسم الطالب يحتوي على كلمة البحث
            if normalized_search in normalized_name:
                print(f"✅ Partial match (student contains search): {student_name}")
                matches.append(student)
            
            # 3. كلمة البحث تحتوي على اسم الطالب
            elif normalized_name in normalized_search and len(normalized_name) > 3:
                print(f"✅ Partial match (search contains student): {student_name}")
                matches.append(student)
        
        # إذا وجدت نتائج متعددة، أعد أولها
        if matches:
            print(f"✅ Returning first of {len(matches)} matches")
            return matches[0]
        
        print(f"❌ No match found for: '{normalized_search}'")
        return None
        
    except Exception as e:
        print(f"❌ Error searching Firebase: {e}")
        return None

# ========== أوامر البوت ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """
🎓 *بوت استرجاع كود الطالب - معهد جيل الأمة*

🔍 *كيفية الاستخدام:*
• أرسل اسمك الكامل كما هو مسجل في المعهد
• سأبحث عنك وأرسل لك الكود

📝 *مثال:* أحمد محمد

🌐 *منصة المعهد:* https://ommah3.vercel.app

📞 *للدعم:* @GM1mohamed
""", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """
🆘 *مساعدة*

📤 *أرسل اسمك الكامل* (مثال: أحمد محمد)

💡 *ملاحظات:*
• البوت يتعامل مع الأخطاء البسيطة
• يمكنك كتابة الاسم بدون تشكيل

📞 *للتواصل:* @GM1mohamed
""", parse_mode='Markdown')

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, """
ℹ️ *عن البوت*

🤖 *الاسم:* بوت استرجاع كود الطالب
🏫 *الجهة:* معهد جيل الأمة
📅 *الإصدار:* 2.0
👨‍💻 *المطور:* GM-mohamed

🔗 *رابط المعهد:* https://ommah3.vercel.app
""", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def send_status(message):
    """التحقق من حالة الاتصال بقاعدة البيانات"""
    if db:
        try:
            students_ref = db.collection('students')
            docs = students_ref.get()
            count = len(list(docs))
            bot.reply_to(message, f"""
✅ *البوت يعمل بشكل طبيعي*

📊 *حالة قاعدة البيانات:* متصلة
👨‍🎓 *عدد الطلاب المسجلين:* {count}
📅 *آخر تحديث:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""", parse_mode='Markdown')
        except:
            bot.reply_to(message, "⚠️ قاعدة البيانات متصلة ولكن حدث خطأ في القراءة")
    else:
        bot.reply_to(message, "❌ قاعدة البيانات غير متصلة")

@bot.message_handler(func=lambda message: True)
def get_code(message):
    """معالجة رسائل المستخدمين (البحث عن الكود)"""
    name = message.text.strip()
    
    # تجاهل الأوامر
    if name.startswith('/'):
        return
    
    # التحقق من طول الاسم
    if len(name) < 3:
        bot.reply_to(message, "❌ الاسم قصير جداً. الرجاء إدخال الاسم الكامل (على الأقل 3 أحرف).")
        return
    
    # إظهار مؤشر الكتابة
    bot.send_chat_action(message.chat.id, 'typing')
    
    # البحث عن الطالب
    student = search_student(name)
    
    if student:
        student_name = student.get('name', 'غير معروف')
        student_code = student.get('code', 'غير متوفر')
        student_level = student.get('overallLevel', 'غير محدد')
        
        bot.reply_to(message, f"""
✅ *تم العثور على حسابك!*

👤 *الاسم:* {student_name}
🔑 *الكود الخاص بك:* `{student_code}`
📊 *المستوى:* {student_level}

🔗 *للدخول إلى المنصة:* https://ommah3.vercel.app

⚠️ *تنبيه:* لا تشارك كودك مع أي شخص آخر.
""", parse_mode='Markdown')
        
        # تسجيل العملية
        print(f"✅ Code sent to: {student_name} ({student_code})")
    else:
        bot.reply_to(message, f"""
❌ *لم يتم العثور على طالب بالاسم:* "{name}"

💡 *تأكد من:*
• كتابة الاسم الكامل (الاسم الأول + اسم العائلة)
• عدم وجود أخطاء إملائية

📝 *مثال:* أحمد محمد

📞 *إذا كنت متأكداً من الاسم:* تواصل مع الإدارة على @GM1mohamed
""", parse_mode='Markdown')
        
        print(f"❌ Student not found: {name}")

# ========== تشغيل البوت ==========
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 بوت استرجاع كود الطالب - معهد جيل الأمة")
    print("=" * 50)
    print(f"📅 بدء التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Bot Token: {BOT_TOKEN[:10]}...")
    print("✅ جاهز لاستقبال الطلبات...")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
