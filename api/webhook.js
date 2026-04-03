// api/webhook.js
import { Telegraf } from 'telegraf';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, query, where, getDocs } from 'firebase/firestore';

// ========== إعدادات Firebase ==========
const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    authDomain: process.env.FIREBASE_AUTH_DOMAIN,
    projectId: process.env.FIREBASE_PROJECT_ID,
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.FIREBASE_APP_ID
};

// ========== إعدادات البوت ==========
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

// تهيئة Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// تهيئة البوت
const bot = new Telegraf(BOT_TOKEN);

// ========== دوال مساعدة ==========
function removeDiacritics(text) {
    const diacritics = /[\u064B-\u065F\u0670]/g;
    return text.replace(diacritics, '');
}

function normalizeText(text) {
    let normalized = text.trim();
    normalized = removeDiacritics(normalized);
    normalized = normalized.replace(/[ىي]/g, 'ي');
    normalized = normalized.replace(/[ةه]/g, 'ه');
    normalized = normalized.replace(/[آإأ]/g, 'ا');
    normalized = normalized.replace(/\s+/g, ' ').trim();
    return normalized;
}

function calculateSimilarity(str1, str2) {
    const norm1 = normalizeText(str1);
    const norm2 = normalizeText(str2);
    if (norm1 === norm2) return 1;
    let matches = 0;
    const maxLength = Math.max(norm1.length, norm2.length);
    for (let i = 0; i < Math.min(norm1.length, norm2.length); i++) {
        if (norm1[i] === norm2[i]) matches++;
    }
    return matches / maxLength;
}

async function searchStudent(searchName) {
    const studentsRef = collection(db, "students");
    const querySnapshot = await getDocs(studentsRef);
    
    const normalizedSearch = normalizeText(searchName);
    const results = [];
    
    for (const doc of querySnapshot.docs) {
        const student = doc.data();
        const normalizedStudentName = normalizeText(student.name);
        
        if (normalizedStudentName === normalizedSearch) {
            return { exact: true, results: [{ id: doc.id, ...student }] };
        }
        
        if (normalizedStudentName.includes(normalizedSearch) || 
            normalizedSearch.includes(normalizedStudentName)) {
            results.push({ id: doc.id, ...student, similarity: 0.8 });
        } else {
            const similarity = calculateSimilarity(student.name, searchName);
            if (similarity > 0.5) {
                results.push({ id: doc.id, ...student, similarity });
            }
        }
    }
    
    results.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
    return { exact: false, results: results.slice(0, 5) };
}

// ========== أوامر البوت ==========
bot.start((ctx) => {
    ctx.reply(
        `🎓 *مرحباً بك في بوت استرجاع كود الطالب*\n\n` +
        `🔍 *كيفية الاستخدام:*\n` +
        `• أرسل اسمك الكامل كما هو مسجل في المعهد\n` +
        `• يمكنك كتابة الاسم بدون تشكيل أو بأخطاء بسيطة\n` +
        `• سأبحث عنك وأرسل لك الكود الخاص بك\n\n` +
        `📝 *مثال:* أحمد محمد\n\n` +
        `🆘 *للحصول على مساعدة:* أرسل /help`,
        { parse_mode: 'Markdown' }
    );
});

bot.help((ctx) => {
    ctx.reply(
        `🆘 *مساعدة استرجاع الكود*\n\n` +
        `📤 *كيفية إرسال الاسم:*\n` +
        `• اكتب اسمك الكامل كما هو مسجل في المعهد\n` +
        `• البوت يتعامل مع الأخطاء الإملائية البسيطة\n\n` +
        `📞 *للتواصل مع الإدارة:* [اضغط هنا](https://t.me/GM1mohamed)\n` +
        `🌐 *منصة المعهد:* [ommah3.vercel.app](https://ommah3.vercel.app)`,
        { parse_mode: 'Markdown', disable_web_page_preview: true }
    );
});

bot.on('text', async (ctx) => {
    const studentName = ctx.message.text.trim();
    
    if (studentName.startsWith('/')) return;
    
    await ctx.sendChatAction('typing');
    
    if (studentName.length < 3) {
        await ctx.reply(
            `❌ *الاسم قصير جداً*\n\n` +
            `الرجاء إدخال الاسم الكامل (على الأقل 3 أحرف).`,
            { parse_mode: 'Markdown' }
        );
        return;
    }
    
    try {
        const searchResult = await searchStudent(studentName);
        
        if (searchResult.results.length === 0) {
            await ctx.reply(
                `❌ *لم يتم العثور على طالب بالاسم:* "${studentName}"\n\n` +
                `💡 *الأسباب المحتملة:*\n` +
                `• تأكد من كتابة الاسم الكامل\n` +
                `• قد يكون الاسم مسجلاً بشكل مختلف\n\n` +
                `📞 *إذا استمرت المشكلة:* تواصل مع الإدارة`,
                { parse_mode: 'Markdown' }
            );
            return;
        }
        
        if (searchResult.results.length === 1) {
            const student = searchResult.results[0];
            await ctx.reply(
                `✅ *تم العثور على حسابك!*\n\n` +
                `👤 *الاسم:* ${student.name}\n` +
                `🔑 *الكود الخاص بك:* \`${student.code}\`\n` +
                `📊 *المستوى:* ${student.overallLevel || 'غير محدد'}\n\n` +
                `🔗 *للدخول إلى المنصة:* [اضغط هنا](https://ommah3.vercel.app)\n\n` +
                `⚠️ *تنبيه:* لا تشارك كودك مع أي شخص آخر.`,
                { parse_mode: 'Markdown', disable_web_page_preview: true }
            );
        } else {
            let message = `⚠️ *تم العثور على ${searchResult.results.length} طالب يحمل اسماً مشابهاً:*\n\n`;
            for (let i = 0; i < searchResult.results.length; i++) {
                const student = searchResult.results[i];
                message += `${i + 1}. ${student.name}\n`;
            }
            message += `\n📝 *يرجى إرسال اسمك الكامل بشكل أكثر دقة.*`;
            await ctx.reply(message, { parse_mode: 'Markdown' });
        }
        
    } catch (error) {
        console.error('خطأ:', error);
        await ctx.reply(
            `❌ *حدث خطأ في النظام*\n\n` +
            `الرجاء المحاولة مرة أخرى لاحقاً.`,
            { parse_mode: 'Markdown' }
        );
    }
});

// ========== معالج Webhook لـ Vercel ==========
export default async function handler(req, res) {
    try {
        // السماح فقط بـ POST من تليجرام
        if (req.method === 'POST') {
            await bot.handleUpdate(req.body, res);
            res.status(200).json({ status: 'ok' });
        } else if (req.method === 'GET') {
            // للتحقق من صحة البوت
            res.status(200).json({ 
                status: 'running',
                message: 'Telegram bot is active!',
                webhook_url: `https://${req.headers.host}/api/webhook`
            });
        } else {
            res.status(405).json({ error: 'Method not allowed' });
        }
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}