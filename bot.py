import os, re, urllib.request, json
from threading import Thread
from flask import Flask
import telebot
from telebot import types

TOKEN = "9022412005:AAE_iuHj950P4MrqFyrcfzWTenT29YM3Shw"
ADMIN_ID = 7516636412
DB_URL = "https://firebaseio.com"
WEB_URL = "https://github.io"

TB_NUM, TB_NAME = "0919946150", "ሞገስ ግርማይ ረዳ"
CBE_NUM, CBE_NAME = "1000786167136", "ሞገስ ግርማይ ረዳ"

app = Flask(__name__)
@app.route('/')
def home():
    return "JOLLY BINGO 24/7 ONLINE!"

bot = telebot.TeleBot(TOKEN)
used_tx, states = set(), {}

def db_get(path):
    try:
        with urllib.request.urlopen(f"{DB_URL}/{path}.json", timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def db_put(path, data):
    try:
        req = urllib.request.Request(f"{DB_URL}/{path}.json", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="PUT")
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def get_bal(uid):
    v = db_get(f"users/{uid}/balance")
    return float(v) if v is not None else 0.0

def set_bal(uid, amount):
    db_put(f"users/{uid}/balance", round(float(amount), 2))

def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🎮 ቢንጎ ተጫወት", "💰 ሂሳብ ሙላ", "💸 ገንዘብ አውጣ", "💳 ቀሪ ሂሳብ")
    return m

@bot.message_handler(commands=['start'])
def start(m):
    u = m.from_user.id
    states.pop(u, None)
    if db_get(f"users/{u}/bonus") is None:
        db_put(f"users/{u}/bonus", True)
        set_bal(u, 10.0)
        msg = "\n🎁 **የ10.00 ብር የመጀመሪያ ቦነስ አግኝተዋል!**\n"
    else:
        msg = ""
    b = get_bal(u)
    bot.send_message(m.chat.id, f"ሰላም {m.from_user.first_name}! 👋{msg}\n💳 ቀሪ ሂሳብዎ: **{b:.2f} ብር**", reply_markup=menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💳 ቀሪ ሂሳብ")
def check_b(m):
    bot.send_message(m.chat.id, f"💳 ቀሪ ሂሳብዎ: **{get_bal(m.from_user.id):.2f} ብር**", reply_markup=menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 ሂሳብ ሙላ")
def dep(m):
    states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, f"💰 ገንዘብ ካስገቡ በኋላ **SMS** ይላኩ፦\n📱 ቴሌብር: `{TB_NUM}` ({TB_NAME})\n🏦 ሲቢኢ: `{CBE_NUM}` ({CBE_NAME})", reply_markup=menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎮 ቢንጎ ተጫወት")
def play(m):
    u = m.from_user.id
    states.pop(u, None)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 JOLLY BINGO ዌብሳይት ክፈት", web_app=types.WebAppInfo(f"{WEB_URL}?uid={u}")))
    bot.send_message(m.chat.id, "🎮 **የቢንጎ መጫወቻ ቦርዱን ለመክፈት ከታች ያለውን ቁልፍ ይጫኑ፦**", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 ገንዘብ አውጣ")
def wd(m):
    u = m.from_user.id
    b = get_bal(u)
    if b < 20:
        bot.send_message(m.chat.id, f"❌ ቢያንስ **20.00 ብር** ያስፈልጋል! ሂሳብዎ: **{b:.2f} ብር**", parse_mode="Markdown")
        return
    states[u] = "WD_AMT"
    bot.send_message(m.chat.id, f"💸 የሚያወጡትን **የብር መጠን** በቁጥር ይጻፉ (ቀሪ: {b:.2f} ብር)፦")

@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def adm(c):
    if c.from_user.id != ADMIN_ID: return
    _, act, uid, amt = c.data.split("_")
    uid, amt = int(uid), float(amt)
    if act == "ok":
        bot.edit_message_text(c.message.text + "\n\n✅ **ተከፍሏል**", c.message.chat.id, c.message.message_id)
        bot.send_message(uid, f"🎉 **{amt:.2f} ብር** ወደ አካውንትዎ ተልኳል!", parse_mode="Markdown")
    else:
        set_bal(uid, get_bal(uid) + amt)
        bot.edit_message_text(c.message.text + "\n\n❌ **ተሰርዟል**", c.message.chat.id, c.message.message_id)
        bot.send_message(uid, f"⚠️ ጥያቄዎ ተሰርዟል፤ **{amt:.2f} ብር** ተመልሷል።", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    u, txt, st = m.from_user.id, m.text.strip(), states.get(m.from_user.id)
    if st == "WD_AMT":
        try:
            a, b = float(txt), get_bal(u)
            if a < 20 or a > b:
                bot.reply_to(m, f"⚠️ ከ 20 እስከ {b:.2f} ብር መካከል ይጻፉ፦")
                return
            states[u] = f"WD_ACC:{a}"
            bot.reply_to(m, "🏦 ባንክ (ቴሌብር/ሲቢኢ)፣ አካውንት ቁጥር እና ስም ይጻፉ፦")
        except ValueError:
            bot.reply_to(m, "⚠️ በቁጥር ብቻ ይጻፉ፦")
        return
    if st and st.startswith("WD_ACC:"):
        a = float(st.split(":"))
        states.pop(u, None)
        set_bal(u, get_bal(u) - a)
        kb = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("✅ ተከፍሏል", callback_data=f"adm_ok_{u}_{a}"),
            types.InlineKeyboardButton("❌ ሰርዝ", callback_data=f"adm_no_{u}_{a}")
        )
        bot.send_message(ADMIN_ID, f"🚨 **Withdraw ጥያቄ!**\n👤 {m.from_user.first_name} (`{u}`)\n💰 **{a:.2f} ብር**\n🏦 {txt}", reply_markup=kb, parse_mode="Markdown")
        bot.reply_to(m, f"✅ የ **{a:.2f} ብር** ጥያቄዎ ለአስተዳዳሪው ደርሷል!", parse_mode="Markdown")
        return

    am = re.search(r'(?:ETB|birr|Birr)\s*([0-9,]+(?:\.[0-9]{1,2})?)|([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:ETB|birr|Birr)', txt)
    tx = re.search(r'(?:transaction number is|Ref No|Txn ID|ID)[:\s]*([A-Z0-9]{8,15})', txt, re.IGNORECASE)
    if am and tx:
        a, t = float((am.group(1) or am.group(2)).replace(',', '')), tx.group(1).upper()
        if t in used_tx:
            bot.reply_to(m, "❌ ይህ ትራንዛክሽን ቀድሞ ጥቅም ላይ ውሏል!")
            return
        used_tx.add(t)
        nb = get_bal(u) + a
        set_bal(u, nb)
        bot.reply_to(m, f"✅ **+{a:.2f} ብር** ተሞልቷል!\n💳 አዲስ ሂሳብ: **{nb:.2f} ብር**", parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, "👇 ከታች ያሉትን ቁልፎች ይጠቀሙ፦", reply_markup=menu())

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
