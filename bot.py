import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import re
import json
import time

BOT_TOKEN = "8788938519:AAEqrkdcAI53XfaDFLzoL_oAVxVh81EknPQ"

# ========== حذف أي Webhook سابق ==========
try:
    bot_temp = telebot.TeleBot(BOT_TOKEN)
    bot_temp.remove_webhook()
    time.sleep(1)
    print("✅ Webhook removed")
except:
    pass

# ========== بيانات Service Account ==========
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
    cred_dict = json.loads(SERVICE_ACCOUNT_JSON)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully")
except Exception as e:
    print(f"❌ Firebase error: {e}")
    db = None

# ========== تهيئة البوت ==========
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()
time.sleep(1)

# ========== دالة تنظيف النص ==========
def normalize_text(text):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('آ', 'ا').replace('إ', 'ا').replace('أ', 'ا')
    text = text.replace('ى', 'ي').replace('ة', 'ه')
    return text

# ========== أمر عرض جميع الطلاب ==========
@bot.message_handler(commands=['list'])
def show_all_students(message):
    if db is None:
        bot.reply_to(message, "❌ قاعدة البيانات غير متصلة")
        return
    
    try:
        students_ref = db.collection('students')
        docs = students_ref.get()
        
        names_list = []
        for doc in docs:
            student = doc.to_dict()
            name = student.get('name', 'بدون اسم')
            code = student.get('code', 'بدون كود')
            level = student.get('overallLevel', 'غير محدد')
            names_list.append(f"📌 *الاسم:* {name}\n   🔑 *الكود:* `{code}`\n   📊 *المستوى:* {level}")
        
        if names_list:
            reply = "📋 *قائمة الطلاب المسجلين في قاعدة البيانات:*\n\n" + "\n\n".join(names_list)
            bot.reply_to(message, reply, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 لا يوجد طلاب مسجلين في قاعدة البيانات")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# ========== أمر معرفة حالة الاتصال ==========
@bot.message_handler(commands=['status'])
def send_status(message):
    if db:
        try:
            students_ref = db.collection('students')
            docs = students_ref.get()
            count = len(list(docs))
            bot.reply_to(message, f"""
✅ *البوت يعمل بشكل طبيعي*

📊 *حالة قاعدة البيانات:* متصلة
👨‍🎓 *عدد الطلاب المسجلين:* {count}

📝 *لرؤية جميع الطلاب:* أرسل /list
""", parse_mode='Markdown')
        except:
            bot.reply_to(message, "⚠️ قاعدة البيانات متصلة ولكن حدث خطأ")
    else:
        bot.reply_to(message, "❌ قاعدة البيانات غير متصلة")

# ========== أمر start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """
🎓 *بوت استرجاع كود الطالب - معهد جيل الأمة*

🔍 *كيفية الاستخدام:*
• أرسل `/list` لرؤية جميع الأسماء المسجلة
• ثم أرسل الاسم كما هو بالضبط

📝 *مثال:* إذا ظهر الاسم "أحمد محمد"، أرسله كما هو

🌐 *منصة المعهد:* https://ommah3.vercel.app
""", parse_mode='Markdown')

# ========== البحث عن الطالب ==========
@bot.message_handler(func=lambda message: True)
def get_code(message):
    name = message.text.strip()
    
    # تجاهل الأوامر
    if name.startswith('/'):
        return
    
    if len(name) < 2:
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    if db is None:
        bot.reply_to(message, "❌ قاعدة البيانات غير متصلة")
        return
    
    try:
        students_ref = db.collection('students')
        docs = students_ref.get()
        
        found = None
        
        for doc in docs:
            student = doc.to_dict()
            student_name = student.get('name', '')
            
            # مقارنة تامة
            if student_name == name:
                found = student
                break
            
            # مقارنة بعد تنظيف النص
            if normalize_text(student_name) == normalize_text(name):
                found = student
                break
        
        if found:
            bot.reply_to(message, f"""
✅ *تم العثور على حسابك!*

👤 *الاسم:* {found.get('name')}
🔑 *الكود:* `{found.get('code')}`
📊 *المستوى:* {found.get('overallLevel', 'غير محدد')}

🔗 https://ommah3.vercel.app
""", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ لم يتم العثور على: {name}\n\n📝 أرسل `/list` لرؤية جميع الأسماء المسجلة")
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# ========== تشغيل البوت ==========
print("=" * 50)
print("🤖 بوت استرجاع كود الطالب")
print("=" * 50)
print("✅ جاهز لاستقبال الطلبات...")
print("📝 الأوامر المتاحة:")
print("   /start - رسالة الترحيب")
print("   /list - عرض جميع الطلاب")
print("   /status - حالة الاتصال")
print("=" * 50)

bot.infinity_polling(timeout=10, long_polling_timeout=5)