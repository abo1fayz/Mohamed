// api/webhook.js
export default async function handler(req, res) {
    console.log("✅ تم استقبال طلب!", req.method);
    res.status(200).json({ status: 'ok', message: 'Bot is working!' });
}
