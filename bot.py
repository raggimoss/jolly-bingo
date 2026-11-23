
import os
import telebot
from telebot import types
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

users = {}

@app.route('/')
def home():
    return "Jolly Bingo Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    
    if user_id not in users:
        users[user_id] = {'balance': 0, 'name': first_name}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Play Bingo"),
        types.KeyboardButton("Balance"),
        types.KeyboardButton("Deposit"),
        types.KeyboardButton("Withdraw")
    )
    

    welcome_text = (
        f"Welcome to Jolly Bingo {first_name}!\n\n"
        f"Your Balance: {users[user_id]['balance']} ETB\n\n"
        "Use the buttons below to start."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'name': message.from_user.first_name}
        
    text = message.text
    
    if text == "Balance":
        bot.reply_to(message, f"Your current 

balance is: {users[user_id]['balance']} ETB.")
        
    elif text == "Deposit":
        deposit_info = (
            "To deposit money, transfer to:\n\n"
            "Telebirr: 09XXXXXXXX\n"
            "CBE: 1000XXXXXXXXX\n\n"
            "After transferring, send the receipt screenshot here."
        )
        bot.reply_to(message, deposit_info)
        
    elif text == "Withdraw":
        if users[user_id]['balance'] < 50:
            bot.reply_to(message, "Minimum withdrawal is 50 ETB.")
        else:
            bot.reply_to(message, "Reply with the amount and your Telebirr phone number.")
            
    elif text == "Play Bingo":

        if users[user_id]['balance'] < 10:
            bot.reply_to(message, "You need at least 10 ETB to play. Please Deposit first!")
        else:
            bot.reply_to(message, "Game starting soon!")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    bot.reply_to(message, "Receipt received! Your balance will be updated shortly.")
    if ADMIN_ID:
        bot.send_message(ADMIN_ID, f"New Deposit Receipt!\nFrom: {first_name}\nID: {user_id}\n\nTo add balance send:\n/add {user_id} 100")

@bot.message_handler(commands=['add'])

def add_balance(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        try:
            parts = message.text.split()
            target_id = parts[1]
            amount = int(parts[2])
            if target_id in users:
                users[target_id]['balance'] += amount
                bot.reply_to(message, f"Added {amount} ETB to user {target_id}.")
                bot.send_message(target_id, f"Congratulations! {amount} ETB has been added to your account.")
            else:
                bot.reply_to(message, "User not found.")
        except:
            bot.reply_to(message, "Usage: /add USER_ID AMOUNT")

if __name__ == "__main__":

    threading.Thread(target=run_web).start()
    bot.infinity_polling()
