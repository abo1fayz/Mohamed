from http.server import BaseHTTPRequestHandler
import telebot
import json
import re
from datetime import datetime

# ========== إعدادات البوت (موجودة مباشرة في الكود) ==========
BOT_TOKEN = "8773180444:AAFqH82a0WHIm6U2RG4knBUG1W2vBvJnSTI"

# ========== بيانات الطلاب التجريبية (للتجربة) ==========
# يمكنك إضافة الطلاب هنا مباشرة
STUDENTS = {
    "أحمد محمد": {"code": "123456", "level": "متقدم"},
    "محمد علي": {"code": "234567", "level": "متوسط"},
    "عبدالله عمر": {"code": "345678", "level": "مبتدئ"},
    "فاطمة الزهراء": {"code": "456789", "level": "متقدم"},
    "عائشة حسن": {"code": "567890", "level": "متوسط"},
}

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# دالة لتنظيف النص (إزالة التشكيل والفراغات الزائدة)
def normalize_text(text):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # إزالة المسافات الزائدة
    text = text.replace('آ', 'ا').replace('إ', 'ا').replace('أ', 'ا')  # توحيد الألف
    text = text.replace('ى', 'ي').replace('ة', 'ه')  # توحيد الياء والتاء
    text = text.replace('ؤ', 'و').replace('ئ', 'ي')  # توحيد الواو والياء
    return text

# دالة للبحث عن الطالب
def search_student(name):
    normalized_search = normalize_text(name)
    
    # البحث المطابق تماماً
    for student_name, data in STUDENTS.items():
        if normalize_text(student_name) == normalized_search:
            return student_name, data['code'], data['level']
    
    # البحث الجزئي
    for student_name, data in STUDENTS.items():
        if normalized_search in normalize_text(student_name):
            return student_name, data['code'], data['level']
    
    return None, None, None

# دالة لإرسال الردود
def send_reply(chat_id, text, parse_mode='Markdown'):
    try:
        bot.send_message(chat_id, text, parse_mode=parse_mode)
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {e}")

# ========== معالج Vercel ==========
class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """الرد على طلبات GET - للتحقق من صحة البوت"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "running",
            "bot": "@student1jilelomaah_bot",
            "message": "البوت يعمل بنجاح! 🎉",
            "students_count": len(STUDENTS),
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """استقبال رسائل تليجرام ومعالجتها"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            # معالجة التحديث
            self.handle_update(update)
            
            # رد بالنجاح
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def handle_update(self, update):
        """معالمة رسائل المستخدمين"""
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        user_name = message['from'].get('first_name', '')
        text = message.get('text', '').strip()
        
        # أمر start
        if text == '/start':
            reply = f"""
🎓 *مرحباً بك في بوت استرجاع كود الطالب* {user_name}

🏫 *معهد جيل الأمة*

🔍 *كيفية الاستخدام:*
• أرسل اسمك الكامل كما هو مسجل في المعهد
• سأبحث عنك وأرسل لك الكود الخاص بك

📝 *مثال:* أحمد محمد

🌐 *منصة المعهد:* https://ommah3.vercel.app

📞 *للدعم:* @GM1mohamed
"""
            send_reply(chat_id, reply)
            return
        
        # أمر help
        if text == '/help':
            reply = """
🆘 *مساعدة استرجاع الكود*

📤 *كيفية إرسال الاسم:*
• اكتب اسمك الكامل (الاسم الأول + اسم العائلة)
• مثال: أحمد محمد
• مثال: محمد علي

💡 *ملاحظة:* البوت يتعامل مع الأخطاء البسيطة

📞 *إذا لم تجد كودك:* تواصل مع الإدارة على @GM1mohamed
"""
            send_reply(chat_id, reply)
            return
        
        # أمر about
        if text == '/about':
            reply = """
ℹ️ *عن البوت*

🤖 *الاسم:* بوت استرجاع كود الطالب
🏫 *الجهة:* معهد جيل الأمة
📅 *الإصدار:* 1.0
👨‍💻 *المطور:* GM-mohamed

🔗 *رابط المعهد:* https://ommah3.vercel.app
"""
            send_reply(chat_id, reply)
            return
        
        # أمر stats (للمشرف فقط)
        if text == '/stats':
            reply = f"""
📊 *إحصائيات البوت*

👨‍🎓 عدد الطلاب المسجلين: {len(STUDENTS)}
✅ حالة البوت: يعمل
📅 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            send_reply(chat_id, reply)
            return
        
        # البحث عن الطالب (إذا كان النص أطول من 3 أحرف وليس أمراً)
        if len(text) >= 3 and not text.startswith('/'):
            self.search_and_reply(chat_id, text)
    
    def search_and_reply(self, chat_id, name):
        """البحث عن الطالب وإرسال الكود"""
        try:
            student_name, code, level = search_student(name)
            
            if student_name:
                reply = f"""
✅ *تم العثور على حسابك!*

👤 *الاسم:* {student_name}
🔑 *الكود الخاص بك:* `{code}`
📊 *المستوى:* {level}

🔗 *للدخول إلى المنصة:* https://ommah3.vercel.app

⚠️ *تنبيه:* لا تشارك كودك مع أي شخص آخر.
"""
                send_reply(chat_id, reply)
                print(f"✅ تم إرسال الكود للطالب: {student_name}")
            else:
                reply = f"""
❌ *لم يتم العثور على طالب بالاسم:* "{name}"

💡 *تأكد من:*
• كتابة الاسم الكامل كما هو مسجل
• عدم وجود أخطاء إملائية

📝 *أمثلة على الأسماء المسجلة:*
{self.get_sample_names()}

📞 *إذا كنت متأكداً من الاسم:* تواصل مع الإدارة على @GM1mohamed
"""
                send_reply(chat_id, reply)
                
        except Exception as e:
            send_reply(chat_id, f"❌ حدث خطأ: {str(e)}")
    
    def get_sample_names(self):
        """إرجاع أمثلة من الأسماء المسجلة"""
        names = list(STUDENTS.keys())
        if len(names) > 3:
            return f"• {names[0]}\n• {names[1]}\n• {names[2]}"
        return "• " + "\n• ".join(names)


# ========== تنبيه: هذا الكود يعمل على Vercel ==========
# لا تحتاج إلى تشغيل bot.infinity_polling() لأن Vercel يستخدم Webhook