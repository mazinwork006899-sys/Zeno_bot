import os, json, threading
from datetime import date
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def get_keyboard():
    kb = [["🎁 المكافأة", "💰 رصيدي"], ["👥 دعوة"]]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = load_data()
    uid = str(update.effective_user.id)
    if uid not in d:
        d[uid] = {"points":0,"last_daily":""}
        save_data(d)
    await update.message.reply_text("مرحبا في Zeno Bot 👋", reply_markup=get_keyboard())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = load_data()
    uid = str(update.effective_user.id)
    if uid not in d:
        d[uid] = {"points":0,"last_daily":""}
    user = d[uid]
    txt = update.message.text
    if "المكافأة" in txt:
        today = str(date.today())
        if user["last_daily"] == today:
            await update.message.reply_text("اخذت مكافأتك اليوم ✅ تعال بكرة")
        else:
            user["points"] += 10
            user["last_daily"] = today
            save_data(d)
            await update.message.reply_text(f"تم! +10 نقاط. رصيدك {user['points']}")
    elif "رصيدي" in txt:
        await update.message.reply_text(f"رصيدك: {user['points']} نقطة 💰")
    elif "دعوة" in txt:
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={uid}"
        await update.message.reply_text(f"رابط دعوتك:\n{link}")
    else:
        await update.message.reply_text("اختار من القائمة 👇", reply_markup=get_keyboard())

app = Flask(__name__)
@app.route("/")
def home(): return "Zeno Bot running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    bot_app.run_polling()
