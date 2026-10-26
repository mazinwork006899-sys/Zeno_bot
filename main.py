import os
import time
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
app_flask = Flask(__name__)

balances = {}
last_daily = {}
referrals = {}

def main_keyboard():
    kb = [
        ["🎁 متجر العروض"],
        ["💎 جمع النقاط", "⭐ شحن رصيد"],
        ["👤 حسابي والإحالة", "ℹ️ مساعدة وقناة"]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in balances:
        balances[uid] = 9
        referrals[uid] = 0
    if context.args and context.args[0].isdigit():
        ref_id = int(context.args[0])
        if ref_id != uid and ref_id in balances:
            balances[ref_id] = balances.get(ref_id, 0) + 2
            referrals[ref_id] = referrals.get(ref_id, 0) + 1
    txt = f"👋 مرحباً بك في بوت Zeno Rewards\n\n🆔 الآيدي: {uid}\n💎 الرصيد: {balances.get(uid,0)}\n\nاختر من القائمة أدناه:"
    await update.message.reply_text(txt, reply_markup=main_keyboard())

async def store_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("💳 بطاقة فيزا حقيقية (10 💎)", callback_data="buy_visa")],
        [InlineKeyboardButton("إغلاق", callback_data="close")]
    ]
    await update.message.reply_text("🎁 متجر العروض والخدمات\n\nاختر الخدمة المطلوبة:", reply_markup=InlineKeyboardMarkup(kb))

async def points_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb = [
        [InlineKeyboardButton("🎁 استلام الهدية اليومية", callback_data="daily")],
        [InlineKeyboardButton("📢 قنوات المهام المتاحة", callback_data="tasks")],
        [InlineKeyboardButton("🎟️ إدخال كود هدية", callback_data="giftcode")],
        [InlineKeyboardButton("إغلاق", callback_data="close")]
    ]
    txt = f"💎 قسم جمع النقاط\n\n💎 رصيدك الحالي: {balances.get(uid,0)}\n\nاختر طريقة كسب النقاط:"
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def charge_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("⭐ 10 -> 10 💎", callback_data="c10"), InlineKeyboardButton("⭐ 15 -> 20 💎", callback_data="c15")],
        [InlineKeyboardButton("⭐ 50 -> 75 💎", callback_data="c50"), InlineKeyboardButton("⭐ 100 -> 150 💎", callback_data="c100")],
        [InlineKeyboardButton("إغلاق", callback_data="close")]
    ]
    await update.message.reply_text("⭐ باقات شحن الرصيد\n\nاختر الباقة:", reply_markup=InlineKeyboardMarkup(kb))

async def balance_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb = [
        [InlineKeyboardButton("🔗 مشاركة الرابط", callback_data="share")],
        [InlineKeyboardButton("🔄 تحديث الرصيد", callback_data="refresh")]
    ]
    link = f"https://t.me/{context.bot.username}?start={uid}"
    txt = f"👤 حسابي والإحالة\n\n🆔 الآيدي: {uid}\n💎 الرصيد: {balances.get(uid,0)}\n👥 الإحالات: {referrals.get(uid,0)}\n\nرابطك:\n{link}"
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def help_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📖 حول البوت", callback_data="about")],
        [InlineKeyboardButton("⭐ دعم البوت (1 ⭐)", callback_data="support")],
        [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq")],
        [InlineKeyboardButton("إغلاق", callback_data="close")]
    ]
    await update.message.reply_text("ℹ️ المساعدة والدعم:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text or ""
    if "متجر العروض" in t:
        await store_sec(update, context)
    elif "جمع النقاط" in t:
        await points_sec(update, context)
    elif "شحن رصيد" in t:
        await charge_sec(update, context)
    elif "حسابي" in t:
        await balance_sec(update, context)
    elif "مساعدة" in t:
        await help_sec(update, context)

async def handle_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()
    if q.data == "close":
        try:
            await q.delete_message()
        except:
            pass
        return
    if q.data == "daily":
        now = time.time()
        last = last_daily.get(uid, 0)
        if now - last < 86400:
            await q.answer("استلمت الهدية اليوم، تعال بكرة", show_alert=True)
            return
        balances[uid] = balances.get(uid, 0) + 15
        last_daily[uid] = now
        await q.edit_message_text(f"✅ تم استلام 15 نقطة\nرصيدك: {balances[uid]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق", callback_data="close")]]))
        return
    if q.data == "buy_visa":
        if balances.get(uid, 0) < 10:
            await q.answer("رصيدك غير كاف، تحتاج 10", show_alert=True)
            return
        balances[uid] -= 10
        await q.edit_message_text(f"✅ تم طلب الفيزا\nرصيدك المتبقي: {balances[uid]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق", callback_data="close")]]))
        return
    if q.data == "refresh":
        await q.edit_message_text(f"💎 رصيدك: {balances.get(uid,0)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق", callback_data="close")]]))
        return
    await q.edit_message_text("قريبا...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق", callback_data="close")]]))

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "🏠 الرئيسية"),
        BotCommand("store", "🎁 متجر العروض"),
        BotCommand("points", "💎 جمع النقاط"),
        BotCommand("charge", "⭐ شحن رصيد"),
        BotCommand("balance", "👤 حسابي"),
        BotCommand("help", "ℹ️ مساعدة"),
    ])

def run_bot():
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("store", store_sec))
    application.add_handler(CommandHandler("points", points_sec))
    application.add_handler(CommandHandler("charge", charge_sec))
    application.add_handler(CommandHandler("balance", balance_sec))
    application.add_handler(CommandHandler("help", help_sec))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_cb))
    application.run_polling()

@app_flask.route('/')
def home():
    return "Zeno Live"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
