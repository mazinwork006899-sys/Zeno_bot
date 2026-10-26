import os, json
from datetime import date
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

TOKEN = os.environ.get("BOT_TOKEN")
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_main_keyboard():
    keyboard = [
        ["🎁 المكافأة اليومية", "💰 رصيدي"],
        ["👥 دعوة الأصدقاء", "🛍️ العروض"],
        ["📊 سجل النقاط", "📋 مهامي"],
        ["🛒 متجر المنتجات", "ℹ️ المساعدة"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    if user_id not in data:
        data[user_id] = {"points": 0, "last_daily": "", "invites": 0}
        if context.args and len(context.args)>0 and context.args[0].startswith("ref_"):
            ref_id = context.args[0].replace("ref_", "")
            if ref_id in data and ref_id != user_id:
                data[ref_id]["points"] += 50
                data[ref_id]["invites"] += 1
        save_data(data)
    await update.message.reply_text(f"أهلاً بك في Zeno!\nرصيدك: {data[user_id]['points']} نقطة", reply_markup=get_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    text = update.message.text
    if user_id not in data:
        data[user_id] = {"points": 0, "last_daily": "", "invites": 0}
    user = data[user_id]
    if "المكافأة اليومية" in text:
        today = str(date.today())
        if user["last_daily"] == today:
            await update.message.reply_text("✅ استلمت مكافأتك اليوم، تعال بكرة!", reply_markup=get_main_keyboard())
        else:
            user["points"] += 10
            user["last_daily"] = today
            save_data(data)
            await update.message.reply_text(f"🎁 مبروك كسبت 10 نقاط!\nرصيدك الآن: {user['points']}", reply_markup=get_main_keyboard())
    elif "رصيدي" in text:
        await update.message.reply_text(f"💰 رصيدك: {user['points']} نقطة\n👥 دعواتك: {user['invites']}", reply_markup=get_main_keyboard())
    elif "دعوة الأصدقاء" in text:
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        await update.message.reply_text(f"📢 رابط دعوتك:\n{link}\n\nكل صديق يدخل = 50 نقطة لك!", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("استخدم الأزرار في الأسفل 👇", reply_markup=get_main_keyboard())

app = Flask(__name__)
@app.route("/")
def home(): return "Zeno Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app_bot.run_polling()
