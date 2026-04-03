// api/webhook.js
import { Telegraf } from 'telegraf';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore';

// ========== قراءة المتغيرات من البيئة (Vercel) ==========
const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    authDomain: process.env.FIREBASE_AUTH_DOMAIN,
    projectId: process.env.FIREBASE_PROJECT_ID,
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.FIREBASE_APP_ID
};

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

// ========== التحقق من وجود المتغيرات ==========
if (!BOT_TOKEN) {
    console.error('❌ TELEGRAM_BOT_TOKEN is not set!');
}
if (!firebaseConfig.projectId) {
    console.error('❌ Firebase config is incomplete!');
}

// تهيئة Firebase
let db;
try {
    const app = initializeApp(firebaseConfig);
    db = getFirestore(app);
    console.log('✅ Firebase initialized successfully');
} catch (error) {
    console.error('❌ Firebase initialization error:', error.message);
}

// تهيئة البوت
const bot = new Telegraf(BOT_TOKEN);

// ========== دوال مساعدة ==========

// دالة لتنظيف النص (إزالة التشكيل والفراغات الزائدة)
function normalizeText(text) {
    if (!text) return '';
    let normalized = text.trim();
    normalized = normalized.replace(/\s+/g, ' '); // إزالة المسافات الزائدة
    normalized = normalized.replace(/[آإأ]/g, 'ا'); // توحيد الألف
    normalized = normalized.replace(/[ىي]/g, 'ي'); // توحيد الياء والألف المقصورة
    normalized = normalized.replace(/[ةه]/g, 'ه'); // توحيد التاء المربوطة
    normalized = normalized.replace(/[ًٌٍِ~ً~ٌ~ٍ~َ~ُ~ّ~ْ]/g, ''); // إزالة التشكيل
    return normalized;
}

// دالة للبحث عن الطالب بالاسم
async function searchStudent(searchName) {
    if (!db) return { found: false, student: null, message: '❌ مشكلة في الاتصال بقاعدة البيانات' };
    
    try {
        const studentsRef = collection(db, "students");
        const snapshot = await getDocs(studentsRef);
        
        if (snapshot.empty) {
            return { found: false, student: null, message: '📭 لا يوجد طلاب مسجلين في النظام حالياً' };
        }
        
        const normalizedSearch = normalizeText(searchName);
        let exactMatch = null;
        let partialMatches = [];
        
        for (const doc of snapshot.docs) {
            const student = doc.data();
            const normalizedName = normalizeText(student.name || '');
            
            // البحث المطابق تماماً
            if (normalizedName === normalizedSearch) {
                exactMatch = student;
                break;
            }
            
            // البحث الجزئي (إذا كان الاسم المدخل جزءاً من الاسم المسجل)
            if (normalizedName.includes(normalizedSearch) || 
                normalizedSearch.includes(normalizedName)) {
                partialMatches.push(student);
            }
        }
        
        if (exactMatch) {
            return { found: true, student: exactMatch, exact: true };
        }
        
        if (partialMatches.length > 0) {
            // إذا وجد نتيجة واحدة جزئية
            if (partialMatches.length === 1) {
                return { found: true, student: partialMatches[0], exact: false };
            }
            // إذا وجد عدة نتائج
            return { found: false, student: null, multiple: true, matches: partialMatches };
        }
        
        return { found: false, student: null };
        
    } catch (error) {
        console.error('Error searching student:', error);
        return { found: false, student: null, message: '❌ حدث خطأ في البحث، حاول مرة أخرى' };
    }
}

// ========== أوامر البوت ==========

// أمر start
bot.start((ctx) => {
    ctx.reply(
        `🎓 *مرحباً بك في بوت استرجاع كود الطالب*\n\n` +
        `🏫 *معهد جيل الأمة*\n\n` +
        `🔍 *كيفية الاستخدام:*\n` +
        `• أرسل اسمك الكامل كما هو مسجل في المعهد\n` +
        `• سأبحث عنك وأرسل لك الكود الخاص بك\n\n` +
        `📝 *مثال:*\n` +
        `أحمد محمد\n\n` +
        `📞 *للدعم والتواصل:* [اضغط هنا](https://t.me/GM1mohamed)\n` +
        `🌐 *منصة المعهد:* [ommah3.vercel.app](https://ommah3.vercel.app)\n\n` +
        `🆘 *للمساعدة:* أرسل /help`,
        { parse_mode: 'Markdown', disable_web_page_preview: true }
    );
});

// أمر help
bot.help((ctx) => {
    ctx.reply(
        `🆘 *مساعدة استرجاع الكود*\n\n` +
        `📤 *كيفية إرسال الاسم:*\n` +
        `• اكتب اسمك الكامل كما هو مسجل في المعهد\n` +
        `• يمكنك كتابة الاسم بدون تشكيل\n` +
        `• البوت يتعامل مع الأخطاء البسيطة\n\n` +
        `✅ *أمثلة صحيحة:*\n` +
        `• أحمد محمد\n` +
        `• محمد علي\n` +
        `• عبدالله عمر\n\n` +
        `📞 *للتواصل مع الإدارة:* [اضغط هنا](https://t.me/GM1mohamed)\n` +
        `🌐 *منصة المعهد:* [ommah3.vercel.app](https://ommah3.vercel.app)`,
        { parse_mode: 'Markdown', disable_web_page_preview: true }
    );
});

// أمر about - معلومات عن البوت
bot.command('about', (ctx) => {
    ctx.reply(
        `ℹ️ *عن البوت*\n\n` +
        `🤖 *الاسم:* بوت استرجاع كود الطالب\n` +
        `🏫 *الجهة:* معهد جيل الأمة\n` +
        `📅 *الإصدار:* 1.0.0\n` +
        `👨‍💻 *المطور:* GM-mohamed\n\n` +
        `🔗 *رابط المعهد:* [ommah3.vercel.app](https://ommah3.vercel.app)`,
        { parse_mode: 'Markdown', disable_web_page_preview: true }
    );
});

// التعامل مع الرسائل النصية (اسم الطالب)
bot.on('text', async (ctx) => {
    const studentName = ctx.message.text.trim();
    
    // تجاهل الأوامر
    if (studentName.startsWith('/')) return;
    
    // إظهار مؤشر الكتابة
    await ctx.sendChatAction('typing');
    
    // التحقق من طول الاسم
    if (studentName.length < 3) {
        await ctx.reply(
            `❌ *الاسم قصير جداً*\n\n` +
            `الرجاء إدخال الاسم الكامل (على الأقل 3 أحرف).\n` +
            `📝 مثال: أحمد محمد`,
            { parse_mode: 'Markdown' }
        );
        return;
    }
    
    try {
        const result = await searchStudent(studentName);
        
        if (result.message) {
            await ctx.reply(result.message);
            return;
        }
        
        if (!result.found) {
            let reply = `❌ *لم يتم العثور على طالب بالاسم:* "${studentName}"\n\n` +
                `💡 *الأسباب المحتملة:*\n` +
                `• تأكد من كتابة الاسم الكامل (الاسم الأول + اسم العائلة)\n` +
                `• قد يكون الاسم مسجلاً بشكل مختلف في النظام\n` +
                `• تأكد من عدم وجود أخطاء إملائية\n\n` +
                `📝 *جرب كتابة الاسم بهذه الطريقة:*\n` +
                `• أحمد محمد (بدون تشكيل)\n` +
                `• محمد أحمد\n\n`;
            
            if (result.multiple && result.matches) {
                reply += `⚠️ *وجدنا عدة أسماء مشابهة:*\n`;
                for (let i = 0; i < Math.min(result.matches.length, 5); i++) {
                    reply += `• ${result.matches[i].name}\n`;
                }
                reply += `\n📝 يرجى إرسال الاسم بشكل أكثر دقة.`;
            }
            
            reply += `\n📞 *إذا استمرت المشكلة:* تواصل مع الإدارة [هنا](https://t.me/GM1mohamed)`;
            
            await ctx.reply(reply, { parse_mode: 'Markdown', disable_web_page_preview: true });
            return;
        }
        
        // تم العثور على الطالب
        const student = result.student;
        const matchType = result.exact ? '✅ *تم العثور على حسابك!*' : '✅ *تم العثور على حساب قريب من اسمك!*';
        
        await ctx.reply(
            `${matchType}\n\n` +
            `👤 *الاسم:* ${student.name}\n` +
            `🔑 *الكود الخاص بك:* \`${student.code}\`\n` +
            `📊 *المستوى:* ${student.overallLevel || 'غير محدد'}\n` +
            `📅 *تاريخ التسجيل:* ${student.createdAt ? new Date(student.createdAt.toDate()).toLocaleDateString('ar-EG') : 'غير محدد'}\n\n` +
            `🔗 *للدخول إلى المنصة:* [اضغط هنا](https://ommah3.vercel.app)\n\n` +
            `⚠️ *تنبيه:* لا تشارك كودك مع أي شخص آخر.`,
            { parse_mode: 'Markdown', disable_web_page_preview: true }
        );
        
        console.log(`✅ تم إرسال الكود للطالب: ${student.name} (${student.code})`);
        
    } catch (error) {
        console.error('Error in text handler:', error);
        await ctx.reply(
            `❌ *حدث خطأ في النظام*\n\n` +
            `الرجاء المحاولة مرة أخرى لاحقاً.\n\n` +
            `📞 *للتواصل مع الدعم الفني:* [اضغط هنا](https://t.me/GM1mohamed)`,
            { parse_mode: 'Markdown', disable_web_page_preview: true }
        );
    }
});

// ========== معالج Webhook لـ Vercel ==========
export default async function handler(req, res) {
    // إضافة CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // التعامل مع طلبات OPTIONS (preflight)
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    try {
        if (req.method === 'POST') {
            // معالجة طلب webhook من تليجرام
            await bot.handleUpdate(req.body, res);
            res.status(200).json({ status: 'ok' });
        } else if (req.method === 'GET') {
            // للتحقق من صحة البوت واختباره
            res.status(200).json({ 
                status: 'running',
                bot: '@student1jilelomaah_bot',
                message: 'البوت يعمل بنجاح! 🎉',
                timestamp: new Date().toISOString(),
                firebase_connected: !!db,
                telegram_token_set: !!BOT_TOKEN
            });
        } else {
            res.status(405).json({ error: 'Method not allowed' });
        }
    } catch (error) {
        console.error('Webhook error:', error);
        res.status(500).json({ error: error.message });
    }
}