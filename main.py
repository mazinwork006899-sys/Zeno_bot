import os
import time
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

# تخزين مؤقت - لو عايز تخزن في ملف بعدين بنعملو
balances = {}
last_daily = {}

def get_main_keyboard():
    keyboard = [
        ["💰 رصيدي", "🎁 المكافأة اليومية"],
        ["📢 العروض", "👥 دعوة الأصدقاء"],
        ["📋 مهامي", "🛍️ متجر المنتجات"],
        ["ℹ️ المساعدة", "📊 سجل النقاط"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in balances:
        balances[uid] = 0
    await update.message.reply_text(
        "اجمع 15 نقطة من المكافأة اليومية مرة كل 24 ساعة.\nاختر من القائمة تحت:",
        reply_markup=get_main_keyboard()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if uid not in balances:
        balances[uid] = 0

    # بدون كيبورد هنا - دا سر الحل
    if "رصيدي" in text:
        await update.message.reply_text(f"رصيدك الحالي: {balances[uid]} نقطة.")
        return

    if "المكافأة اليومية" in text:
        now = time.time()
        last = last_daily.get(uid, 0)
        if now - last < 24*3600:
            remain = 24*3600 - (now-last)
            h = int(remain//3600)
            m = int((remain%3600)//60)
            await update.message.reply_text(f"لقد استلمت المكافأة اليومية بالفعل. حاول بعد نحو {h} ساعة و {m} دقيقة.")
            return
        balances[uid] += 15
        last_daily[uid] = now
        await update.message.reply_text(f"تم! استلمت 15 نقطة. رصيدك الآن {balances[uid]} نقطة.")
        return

    if "العروض" in text:
        await update.message.reply_text("لا توجد عروض متاحة حالياً.")
        return

    if "متجر" in text:
        await update.message.reply_text("لا توجد منتجات متاحة حالياً.")
        return

    if "مهامي" in text:
        await update.message.reply_text("لا توجد مهام متاحة حالياً.")
        return

    if "دعوة" in text:
        await update.message.reply_text(f"رابط دعوتك: https://t.me/{context.bot.username}?start={uid}")
        return

    if "سجل النقاط" in text:
        await update.message.reply_text(f"سجل نقاطك: {balances[uid]} نقطة من المكافأة اليومية.")
        return

    if "المساعدة" in text:
        await update.message.reply_text("للمساعدة تواصل مع المشرف.")
        return

async def post_init(application):
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands([BotCommand("start","بدء")])

def run_bot():
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()

@app.route('/')
def home():
    return "Zeno Live"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
