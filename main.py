import os
import threading
from flask import Flask
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

# === هنا تعدل الأوامر العايزها تظهر في قائمة تليجرام ===
MY_COMMANDS = [
    BotCommand("start", "🚀 بدء البوت"),
    BotCommand("help", "❓ المساعدة"),
    BotCommand("id", "🆔 معرفي"),
]

# === الهاندلرز ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"أهلا {update.effective_user.first_name} 👋\nالبوت شغال تمام!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("الأوامر:\n/start - بدء\n/help - مساعدة\n/id - معرفك")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"الـ ID بتاعك: {update.effective_user.id}")

# دا بحل مشكلة تكرار القائمة
async def post_init(application):
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands(MY_COMMANDS)
    print("Commands set successfully")

def run_bot():
    if not TOKEN:
        print("ERROR: BOT_TOKEN not set!")
        return
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("id", id_cmd))
    print("Bot polling started...")
    application.run_polling()

@app.route('/')
def home():
    return "Zeno Bot is Live ✅"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
