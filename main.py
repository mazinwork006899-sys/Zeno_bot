import os, time, threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

balances = {}
last_daily = {}
referrals = {}

# الكيبورد الثابت التحت - زي GoldenPlay بالضبط وما بيتكرر
def main_keyboard():
    keyboard = [
        ["🎁 متجر العروض"],
        ["💎 جمع النقاط", "⭐ شحن رصيد"],
        ["👤 حسابي والإحالة", "ℹ️ مساعدة وقناة"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def format_balance(uid):
    return balances.get(uid, 0)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in balances:
        balances[uid] = 9 # نفس ما في الصورة 9
        referrals[uid] = 0
    
    # لو جاي برابط احالة
    if context.args and context.args[0].isdigit():
        ref_id = int(context.args[0])
        if ref_id != uid and ref_id in balances:
            balances[ref_id] = balances.get(ref_id, 0) + 2
            referrals[ref_id] = referrals.get(ref_id, 0) + 1

    text = f"👋 مرحباً بك في بوت Zeno Rewards\n\n🆔 الآيدي: {uid}\n💎 الرصيد: {format_balance(uid)}\n\nاختر من القائمة أدناه:"
    await update.message.reply_text(text, reply_markup=main_keyboard())

# متجر العروض - عروضك انت ما اتغيرت
async def store_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 بطاقة فيزا حقيقية (10 💎)", callback_data="buy_visa")],
        [InlineKeyboardButton("إغلاق", callback_data="close")]
    ]
    text = "🎁 متجر العروض والخدمات\n\nاختر الخدمة المطلوبة من القائمة أدناه:"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# جمع النقاط
async def points_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    bal = format_balance(uid)
    keyboard = [
       
