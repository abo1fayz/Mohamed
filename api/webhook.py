from http.server import BaseHTTPRequestHandler
import telebot
import json
import re
from firebase_admin import credentials, firestore, initialize_app

# ========== إعدادات البوت ==========
BOT_TOKEN = "8773180444:AAFqH82a0WHIm6U2RG4knBUG1W2vBvJnSTI"

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# دالة لتنظيف النص
def normalize_text(text):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('آ', 'ا').replace('إ', 'ا').replace('أ', 'ا')
    text = text.replace('ى', 'ي').replace('ة', 'ه')
    return text

# ========== معالج Vercel ==========
class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """الرد على طلبات GET للتحقق من صحة البوت"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "status": "running",
            "bot": "@student1jilelomaah_bot",
            "message": "البوت يعمل بنجاح!"
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        """استقبال رسائل تليجرام ومعالجتها"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = json.loads(post_data.decode('utf-8'))
        
        # معالجة التحديث
        self.handle_update(update)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
    
    def handle_update(self, update):
        """معالمة رسائل المستخدمين"""
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # أمر start
        if text == '/start':
            bot.send_message(chat_id, """
🎓 *بوت استرجاع كود الطالب*

🔍 أرسل اسمك الكامل وسأبحث عن الكود.

📝 مثال: أحمد محمد
""", parse_mode='Markdown')
            return
        
        # أمر help
        if text == '/help':
            bot.send_message(chat_id, """
🆘 *مساعدة*

📤 أرسل اسمك الكامل (مثال: أحمد محمد)
📞 للتواصل: @GM1mohamed
""", parse_mode='Markdown')
            return
        
        # البحث عن الطالب
        if len(text) > 3 and not text.startswith('/'):
            self.search_and_reply(chat_id, text)
    
    def search_and_reply(self, chat_id, name):
        """البحث عن الطالب وإرسال الكود"""
        # هنا يمكنك إضافة الاتصال بقاعدة البيانات
        # حالياً نرسل رداً تجريبياً
        bot.send_message(chat_id, f"""
🔍 *جاري البحث عن:* {name}

⚠️ البوت قيد التهيئة...
📞 للتواصل: @GM1mohamed
""", parse_mode='Markdown')