import telebot

BOT_TOKEN = "8773180444:AAFqH82a0WHIm6U2RG4knBUG1W2vBvJnSTI"

bot = telebot.TeleBot(BOT_TOKEN)

# بيانات الطلاب (يمكنك إضافة المزيد)
STUDENTS = {
    "أحمد محمد": "123456",
    "محمد علي": "234567",
    "عبدالله عمر": "345678",
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎓 أرسل اسمك الكامل لاسترجاع الكود")

@bot.message_handler(func=lambda message: True)
def get_code(message):
    name = message.text.strip()
    
    if name in STUDENTS:
        code = STUDENTS[name]
        bot.reply_to(message, f"✅ مرحباً {name}\n🔑 كودك: {code}")
    else:
        bot.reply_to(message, f"❌ لم يتم العثور على: {name}\n\nتأكد من كتابة الاسم كاملاً")

print("🤖 البوت يعمل...")
bot.infinity_polling()