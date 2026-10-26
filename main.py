import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="daily"),
         InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
        [InlineKeyboardButton("👥 دعوة الأصدقاء", callback_data="invite"),
         InlineKeyboardButton("📢 العروض", callback_data="offers")],
        [InlineKeyboardButton("🛍️ متجر المنتجات", callback_data="shop"),
         InlineKeyboardButton("📋 مهامي", callback_data="tasks")],
        [InlineKeyboardButton("📊 سجل النقاط", callback_data="log"),
         InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "اجمع 15 نقطة من المكافأة اليومية مرة كل 24 ساعة.\n"
        "تُضاف نقاط المهام بعد مراجعة الإثباتات واعتماده من المشرف.\n\n"
        "اضغط «🎁 ابدأ» لعرض الخيارات."
    )
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎁 ابدأ", callback_data="main")]])
    await update.message.reply_text(text, reply_markup=btn)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # مهم جداً عشان ما يعلق ويكرر

    data = query.data

    if data == "main":
        await query.message.reply_text("اختر ما تريد من القائمة:", reply_markup=main_keyboard())
        return

    if data == "offers":
        # هنا كان التكرار - كنا بنرسل رسالتين مع كيبورد
        # الصح: رسالة واحدة بس بدون كيبورد جديد
        await query.message.reply_text("لا توجد عروض متاحة حالياً. ستتوفر عروض جديدة لاحقاً.")
        return

    if data == "shop":
        await query.message.reply_text("لا توجد منتجات متاحة حالياً. ستظهر المنتجات بعد أن يضيفها المشرف ويؤكد توفر مخزون فعلي.")
        return

    if data == "balance":
        await query.message.reply_text("💰 رصيدك الحالي: 0 نقطة")
        return

    if data == "daily":
        await query.message.reply_text("🎁 تم جمع 15 نقطة! تعال بعد 24 ساعة.")
        return

    # باقي الازرار
    await query.message.reply_text(f"تم اختيار: {data}")

async def post_init(application):
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands([BotCommand("start","بدء البوت")])

def run_bot():
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

@app.route('/')
def home():
    return "Zeno Rewards Live ✅"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
