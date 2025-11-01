import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import logging

# === Log sozlamalari (Railway loglarda ko‘rinishi uchun) ===
logging.basicConfig(level=logging.INFO)

# === Sozlamalar ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token Railway Variables orqali olinadi
ADMIN_ID = 6234736126
CARD_NUMBER = "9860 1678 2074 3752"
CARD_OWNER = "I. TORAXON"
CHANNEL_USERNAME = "@premum_uc_hizmati"

# === Xizmatlar ===
SERVICES = {
    "premium": {
        "name": "Telegram Premium ⭐",
        "tariffs": {"1 oy": 52000, "3 oy": 200000, "12 oy": 400000}
    },
    "stars": {
        "name": "Telegram Stars ✨",
        "tariffs": {"100⭐": 26000, "250⭐": 60000, "1000⭐": 240000}
    },
    "mlbb": {
        "name": "Mobile Legends 💎",
        "tariffs": {"86💎": 25000, "172💎": 47000, "257💎": 70000, "514💎": 135000, "1000💎": 260000}
    },
    "uc": {
        "name": "PUBG UC 🎮",
        "tariffs": {"60 UC": 13000, "325 UC": 65000, "660 UC": 120000, "1800 UC": 300000, "3850 UC": 590000}
    }
}

bot = telebot.TeleBot(BOT_TOKEN)

# === Helper funksiyalar ===
def format_amount(amount_int):
    return f"{amount_int:,}".replace(",", " ") + " so'm"

def parse_amount(text):
    cleaned = re.sub(r"[^\d]", "", text or "")
    if not cleaned:
        return None
    try:
        val = int(cleaned)
        if val > 0:
            return val
    except:
        return None
    return None

# === Kanalga obuna tekshiruvi ===
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

# === Start buyrug‘i ===
@bot.message_handler(commands=["start"])
def start(message):
    if not check_subscription(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(
            message.chat.id,
            f"👋 Assalomu alaykum! Botdan foydalanish uchun avval {CHANNEL_USERNAME} kanaliga obuna bo‘ling!",
            reply_markup=kb,
        )
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⭐ Telegram Premium", callback_data="service:premium"))
    kb.add(InlineKeyboardButton("✨ Telegram Stars", callback_data="service:stars"))
    kb.add(InlineKeyboardButton("💎 Mobile Legends", callback_data="service:mlbb"))
    kb.add(InlineKeyboardButton("🎮 PUBG UC", callback_data="service:uc"))
    bot.send_message(
        message.chat.id,
        "🤖 <b>Assalomu alaykum!</b>\nBotimizga xush kelibsiz!\nQuyidagi xizmatlardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=kb
    )

# === Xizmat tanlash ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("service:"))
def handle_service(call):
    service_code = call.data.split(":")[1]
    service = SERVICES[service_code]
    kb = InlineKeyboardMarkup()
    for tariff, price in service["tariffs"].items():
        kb.add(InlineKeyboardButton(f"{tariff} - {format_amount(price)}", callback_data=f"tariff:{service_code}:{tariff}:{price}"))
    bot.send_message(call.message.chat.id, f"{service['name']} uchun tarifni tanlang 👇", reply_markup=kb)

# === Tarif tanlandi ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("tariff:"))
def handle_tariff(call):
    _, service_code, tariff, price = call.data.split(":")
    send_payment_info(call.message.chat.id, service_code, int(price), tariff)

# === To‘lov ma’lumotlari ===
def send_payment_info(chat_id, service_code, amount_int, tariff_name):
    service = SERVICES[service_code]
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Men to‘lov qildim", callback_data=f"paid:{service_code}:{amount_int}:{tariff_name}"))

    text = (
        f"💳 <b>{service['name']}</b> uchun to‘lov ma’lumotlari:\n\n"
        f"🔹 Tarif: {tariff_name}\n"
        f"💵 To‘lanadigan summa: <b>{format_amount(amount_int)}</b>\n\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: {CARD_OWNER}\n\n"
        f"✅ To‘lovni amalga oshirgach, 'Men to‘lov qildim' tugmasini bosing."
    )
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)

# === "Men to‘lov qildim" ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("paid:"))
def handle_paid(call):
    _, service_code, amount_raw, tariff_name = call.data.split(":")
    amount_int = int(amount_raw)
    bot.send_message(
        call.message.chat.id,
        "📸 Iltimos, to‘lov chekingizni shu yerga yuboring (rasm sifatida)."
    )
    bot.register_next_step_handler(call.message, process_check_photo, service_code, amount_int, tariff_name)

# === Chek rasm yuborish ===
def process_check_photo(message, service_code, amount_int, tariff_name):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Iltimos, rasm yuboring!")
        bot.register_next_step_handler(message, process_check_photo, service_code, amount_int, tariff_name)
        return

    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✅ Rahmat! Chekingiz yuborildi, maʼlumot tekshirilmoqda.")

    # Chekni admin'ga yuborish
    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=(
            f"📩 Yangi to‘lov!\n\n"
            f"🔹 Xizmat: {SERVICES[service_code]['name']}\n"
            f"📦 Tarif: {tariff_name}\n"
            f"💵 Summasi: {format_amount(amount_int)}\n\n"
            f"👤 Foydalanuvchi: @{message.from_user.username or '—'} (id: {message.from_user.id})"
        ),
    )

# === Run ===
print("🤖 Bot Railway’da ishga tushdi...")
bot.infinity_polling(skip_pending=True)
