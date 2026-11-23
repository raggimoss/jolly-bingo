
import os
import telebot
from telebot import types
from flask import Flask
import threading

# ከሰርቨሩ ላይ Token እና Admin ID ይወስዳል
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ጊዜያዊ የተጫዋቾች መረጃ ማስቀመጫ (በኋላ ወደ Database እንቀይረዋለን)
users = {}

@app.route('/')
def home():
    return "Jolly Bingo Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# /start ሲነካ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    
    if user_id not in users:
        users[user_id] = {'balance': 0, 'name': first_name}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_play = types.KeyboardButton("🎲 ጨዋታ ጀምር (Play)")
    btn_balance = 

types.KeyboardButton("💰 ባላንስ (Balance)")
    btn_deposit = types.KeyboardButton("➕ ብር አስገባ (Deposit)")
    btn_withdraw = types.KeyboardButton("➖ ብር አውጣ (Withdraw)")
    markup.add(btn_play, btn_balance, btn_deposit, btn_withdraw)
    
    welcome_text = (
        f"👋 እንኳን ወደ **Jolly Bingo** በደህና መጡ {first_name}!\n\n"
        f"💵 የእርስዎ ባላንስ: **{users[user_id]['balance']} ብር**\n\n"
        "ለመጫወት ከታች ያሉትን ቁልፎች ይጠቀሙ።"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ቁልፎች ሲነኩ

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'name': message.from_user.first_name}
        
    text = message.text
    
    if text == "💰 ባላንስ (Balance)":
        bot.reply_to(message, f"💵 የአሁኑ ባላንስዎ: **{users[user_id]['balance']} ብር** ነው።", parse_mode="Markdown")
        
    elif text == "➕ ብር አስገባ (Deposit)":
        deposit_info = (
            "💳 **ብር ለማስገባት የሚከተሉትን አካውንቶች ይጠቀሙ፦**\n\n"
            "📱 **Telebirr:** `09XXXXXXXX` (ስምዎ)\n"
            "🏦 **CBE:** `1000XXXXXXXXX` 

(ስምዎ)\n\n"
            "⚠️ ብሩን ከላኩ በኋላ የደረሰኙን ፎቶ (Screenshot) እዚህ ጋር ይላኩ። ሲረጋገጥ ወዲያውኑ ባላንስዎ ላይ ይገባል።"
        )
        bot.reply_to(message, deposit_info, parse_mode="Markdown")
        
    elif text == "➖ ብር አውጣ (Withdraw)":
        if users[user_id]['balance'] < 50:
            bot.reply_to(message, "❌ ብር ለማውጣት ቢያንስ **50 ብር** ባላንስ ሊኖርዎት ይገባል።", parse_mode="Markdown")
        else:
            bot.reply_to(message, "✅ የሚያወጡትን የብር መጠን እና የቴሌብር ስልክ ቁጥርዎን ይጻፉ።")
            
    elif text == "🎲 ጨዋታ ጀምር (Play)":
        if users[user_id]['balance'] < 10:
            bot.reply_to(message, "❌ ለመጫወት ቢያንስ **10 ብር** ሊኖርዎት ይገባል። እባክዎ 

መጀመሪያ ብር ያስገቡ!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "🎉 ጨዋታው በቅርቡ ይጀምራል! (በቀጣይ ደረጃ የቢንጎ ካርቴላውን እንጨምራለን)")

# ተጫዋች የደረሰኝ ፎቶ ሲልክ ወደ እርስዎ (Admin) እንዲልክ
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    bot.reply_to(message, "✅ ደረሰኝዎ ደርሶናል! በጥቂት ደቂቃዎች ውስጥ ተረጋግጦ ባላንስዎ ይሞላል።")
    if ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 አዲስ የክፍያ ደረሰኝ!\nከተጫዋች: {first_name}\nID: `{user_id}`\n\nብር ለመጨመር ይህን ይላኩ:\n`/add {user_id} 100`", 

parse_mode="Markdown")

# እርስዎ (Admin) ለተጫዋች ብር የሚጨምሩበት ትዕዛዝ (ለምሳሌ: /add 12345678 100)
@bot.message_handler(commands=['add'])
def add_balance(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        try:
            parts = message.text.split()
            target_id = parts[1]
            amount = int(parts[2])
            if target_id in users:
                users[target_id]['balance'] += amount
                bot.reply_to(message, f"✅ ለተጫዋች `{target_id}` **{amount} ብር** በተሳካ ሁኔታ ተጨምሯል።", parse_mode="Markdown")
                bot.send_message(target_id, f"🎉 እንኳን ደስ አለዎት! **{amount} ብር** ወደ አካውንትዎ ገብቷል።", 

parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ ተጫዋቹ አልተገኘም።")
        except:
            bot.reply_to(message, "❌ አጠቃቀም: `/add USER_ID AMOUNT`", parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
