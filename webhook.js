// webhook.js - ضع هذا الملف في جذر المشروع مباشرة
import { Telegraf } from 'telegraf';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore';

// ========== المفاتيح مباشرة (للاختبار فقط) ==========
const firebaseConfig = {
    apiKey: "AIzaSyCR3OrzFXKiG2lPNra5OVe2JIN4cI8qBzg",
    authDomain: "omaah-e3c65.firebaseapp.com",
    projectId: "omaah-e3c65",
    storageBucket: "omaah-e3c65.firebasestorage.app",
    messagingSenderId: "942436888350",
    appId: "1:942436888350:web:0f048b2df08bf332c9630f"
};

const BOT_TOKEN = "8773180444:AAFqH82a0WHIm6U2RG4knBUG1W2vBvJnSTI";

// ========== التحقق من المفاتيح ==========
console.log('🔑 Firebase Config:', {
    projectId: firebaseConfig.projectId,
    hasApiKey: !!firebaseConfig.apiKey,
    hasAuthDomain: !!firebaseConfig.authDomain
});
console.log('🤖 Bot Token exists:', !!BOT_TOKEN);

// تهيئة Firebase
let db = null;
let initError = null;

try {
    const app = initializeApp(firebaseConfig);
    db = getFirestore(app);
    console.log('✅ Firebase initialized successfully');
} catch (error) {
    initError = error;
    console.error('❌ Firebase initialization error:', error.message);
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

// اختبار الاتصال بقاعدة البيانات
bot.command('testdb', async (ctx) => {
    if (!db) {
        await ctx.reply(`❌ قاعدة البيانات غير متصلة: ${initError?.message || 'خطأ غير معروف'}`);
        return;
    }
    
    try {
        const studentsRef = collection(db, "students");
        const snapshot = await getDocs(studentsRef);
        await ctx.reply(`✅ قاعدة البيانات متصلة بنجاح!\n📊 عدد الطلاب: ${snapshot.size}`);
    } catch (error) {
        await ctx.reply(`❌ خطأ في الاتصال بقاعدة البيانات: ${error.message}`);
    }
});

// البحث عن الطالب
bot.on('text', async (ctx) => {
    const studentName = ctx.message.text.trim();
    
    // تجاهل الأوامر
    if (studentName.startsWith('/')) return;
    
    // التحقق من اتصال قاعدة البيانات
    if (!db) {
        await ctx.reply(`❌ عذراً، قاعدة البيانات غير متصلة حالياً. الرجاء المحاولة لاحقاً.\n\nالخطأ: ${initError?.message || 'غير معروف'}`);
        return;
    }
    
    await ctx.sendChatAction('typing');
    
    if (studentName.length < 3) {
        await ctx.reply(`❌ الاسم قصير جداً، الرجاء إدخال الاسم الكامل (على الأقل 3 أحرف).`);
        return;
    }
    
    try {
        console.log(`🔍 Searching for: ${studentName}`);
        
        const studentsRef = collection(db, "students");
        const snapshot = await getDocs(studentsRef);
        
        console.log(`📊 Found ${snapshot.size} students in database`);
        
        const normalizedSearch = normalizeText(studentName);
        let foundStudent = null;
        
        for (const doc of snapshot.docs) {
            const student = doc.data();
            const normalizedName = normalizeText(student.name || '');
            
            console.log(`  Comparing: "${normalizedName}" with "${normalizedSearch}"`);
            
            if (normalizedName === normalizedSearch || 
                normalizedName.includes(normalizedSearch) ||
                normalizedSearch.includes(normalizedName)) {
                foundStudent = student;
                console.log(`  ✅ Match found: ${student.name}`);
                break;
            }
        }
        
        if (foundStudent) {
            await ctx.reply(
                `✅ *تم العثور على حسابك!*\n\n` +
                `👤 *الاسم:* ${foundStudent.name}\n` +
                `🔑 *الكود الخاص بك:* \`${foundStudent.code}\`\n` +
                `📊 *المستوى:* ${foundStudent.overallLevel || 'غير محدد'}\n\n` +
                `🔗 *للدخول إلى المنصة:* [ommah3.vercel.app](https://ommah3.vercel.app)\n\n` +
                `⚠️ *تنبيه:* لا تشارك كودك مع أي شخص آخر.`,
                { parse_mode: 'Markdown', disable_web_page_preview: true }
            );
            console.log(`✅ Code sent to ${foundStudent.name}`);
        } else {
            await ctx.reply(
                `❌ *لم يتم العثور على طالب بالاسم:* "${studentName}"\n\n` +
                `💡 *تأكد من:*\n` +
                `• كتابة الاسم الكامل (الاسم الأول + اسم العائلة)\n` +
                `• عدم وجود أخطاء إملائية\n` +
                `• الاسم مطابق لما هو مسجل في المعهد\n\n` +
                `📞 *إذا استمرت المشكلة:* تواصل مع الإدارة [هنا](https://t.me/GM1mohamed)`,
                { parse_mode: 'Markdown' }
            );
            console.log(`❌ No student found for: ${studentName}`);
        }
        
    } catch (error) {
        console.error('Error in search:', error);
        await ctx.reply(
            `❌ *حدث خطأ في البحث*\n\n` +
            `الخطأ: ${error.message}\n\n` +
            `الرجاء المحاولة مرة أخرى لاحقاً.`,
            { parse_mode: 'Markdown' }
        );
    }
});

// ========== معالج Vercel ==========
export default async function handler(req, res) {
    // إضافة CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method === 'POST') {
        try {
            await bot.handleUpdate(req.body, res);
            res.status(200).json({ status: 'ok' });
        } catch (error) {
            console.error('Webhook error:', error);
            res.status(500).json({ error: error.message });
        }
    } else if (req.method === 'GET') {
        res.status(200).json({ 
            status: 'running', 
            bot: '@student1jilelomaah_bot',
            message: 'البوت يعمل! 🎉',
            firebase_connected: db !== null,
            timestamp: new Date().toISOString()
        });
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}