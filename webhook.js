// webhook.js - ضع هذا الملف في جذر المشروع مباشرة
import { Telegraf } from 'telegraf';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore';

// ========== إعدادات Firebase ==========
const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    authDomain: process.env.FIREBASE_AUTH_DOMAIN,
    projectId: process.env.FIREBASE_PROJECT_ID,
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.FIREBASE_APP_ID
};

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

// تهيئة Firebase
let db;
try {
    const app = initializeApp(firebaseConfig);
    db = getFirestore(app);
    console.log('✅ Firebase initialized');
} catch (error) {
    console.error('❌ Firebase error:', error.message);
}

// تهيئة البوت
const bot = new Telegraf(BOT_TOKEN);

// دالة لتنظيف النص
function normalizeText(text) {
    if (!text) return '';
    let normalized = text.trim();
    normalized = normalized.replace(/\s+/g, ' ');
    normalized = normalized.replace(/[آإأ]/g, 'ا');
    normalized = normalized.replace(/[ىي]/g, 'ي');
    normalized = normalized.replace(/[ةه]/g, 'ه');
    return normalized;
}

// أمر start
bot.start((ctx) => {
    ctx.reply(
        `🎓 *مرحباً بك في بوت استرجاع كود الطالب*\n\n` +
        `🔍 *كيفية الاستخدام:*\n` +
        `• أرسل اسمك الكامل كما هو مسجل في المعهد\n` +
        `• سأبحث عنك وأرسل لك الكود الخاص بك\n\n` +
        `📝 *مثال:* أحمد محمد\n\n` +
        `🌐 *منصة المعهد:* [ommah3.vercel.app](https://ommah3.vercel.app)`,
        { parse_mode: 'Markdown', disable_web_page_preview: true }
    );
});

// أمر help
bot.help((ctx) => {
    ctx.reply(
        `🆘 *مساعدة*\n\n` +
        `📤 أرسل اسمك الكامل (مثال: أحمد محمد)\n` +
        `📞 للتواصل مع الإدارة: [اضغط هنا](https://t.me/GM1mohamed)`,
        { parse_mode: 'Markdown' }
    );
});

// البحث عن الطالب
bot.on('text', async (ctx) => {
    const studentName = ctx.message.text.trim();
    if (studentName.startsWith('/')) return;
    
    await ctx.sendChatAction('typing');
    
    if (studentName.length < 3) {
        await ctx.reply(`❌ الاسم قصير جداً، الرجاء إدخال الاسم الكامل.`);
        return;
    }
    
    try {
        const studentsRef = collection(db, "students");
        const snapshot = await getDocs(studentsRef);
        
        const normalizedSearch = normalizeText(studentName);
        let foundStudent = null;
        
        for (const doc of snapshot.docs) {
            const student = doc.data();
            const normalizedName = normalizeText(student.name || '');
            
            if (normalizedName === normalizedSearch || 
                normalizedName.includes(normalizedSearch)) {
                foundStudent = student;
                break;
            }
        }
        
        if (foundStudent) {
            await ctx.reply(
                `✅ *تم العثور على حسابك!*\n\n` +
                `👤 *الاسم:* ${foundStudent.name}\n` +
                `🔑 *الكود:* \`${foundStudent.code}\`\n` +
                `📊 *المستوى:* ${foundStudent.overallLevel || 'غير محدد'}\n\n` +
                `🔗 *للدخول:* [ommah3.vercel.app](https://ommah3.vercel.app)`,
                { parse_mode: 'Markdown', disable_web_page_preview: true }
            );
        } else {
            await ctx.reply(
                `❌ *لم يتم العثور على طالب بالاسم:* "${studentName}"\n\n` +
                `💡 تأكد من كتابة الاسم الكامل كما هو مسجل في المعهد.\n\n` +
                `📞 للتواصل مع الإدارة: [اضغط هنا](https://t.me/GM1mohamed)`,
                { parse_mode: 'Markdown' }
            );
        }
        
    } catch (error) {
        console.error('Error:', error);
        await ctx.reply(`❌ حدث خطأ، الرجاء المحاولة مرة أخرى.`);
    }
});

// ========== معالج Vercel ==========
export default async function handler(req, res) {
    // إضافة CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method === 'POST') {
        try {
            await bot.handleUpdate(req.body, res);
            res.status(200).json({ status: 'ok' });
        } catch (error) {
            console.error('Error:', error);
            res.status(500).json({ error: error.message });
        }
    } else if (req.method === 'GET') {
        res.status(200).json({ 
            status: 'running', 
            bot: '@student1jilelomaah_bot',
            message: 'البوت يعمل! 🎉'
        });
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}