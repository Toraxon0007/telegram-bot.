import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

# === Sozlamalar ===
BOT_TOKEN = "8114837659:"
ADMIN_ID = 6234736126
CARD_NUMBER = "9860 1678 2074 3752"
CARD_OWNER = "I. TORAXON"

# === Xizmatlar ===
SERVICES = {
    "premium": {
        "name": "Telegram Premium ⭐",
        "tariffs": {
            "1oy": 52000,
            "3oy": 200000,
            "12oy": 400000
        }
    },
    "stars": {
        "name": "Telegram Stars ✨",
        "tariffs": {
            "100⭐": 26000,
            "250⭐": 60000,
            "1000⭐": 240000
        }
    },
    "mlbb": {
        "name": "Mobile Legends 💎",
        "tariffs": {
            "86💎": 25000,
            "172💎": 47000,
            "257💎": 70000,
            "514💎": 135000,
            "1000💎": 260000
        }
    },
    "uc": {
        "name": "PUBG UC 🎮",
        "tariffs": {
            "60 UC": 13000,
            "325 UC": 65000,
            "660 UC": 120000,
            "1800 UC": 300000,
            "3850 UC": 590000
        }
    }
}

bot = telebot.TeleBot(BOT_TOKEN)

# --- Helper ---
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

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⭐ Telegram Premium", callback_data="service:premium"))
    kb.add(InlineKeyboardButton("✨ Telegram Stars", callback_data="service:stars"))
    kb.add(InlineKeyboardButton("💎 Mobile Legends", callback_data="service:mlbb"))
    kb.add(InlineKeyboardButton("🎮 PUBG UC", callback_data="service:uc"))

    bot.send_message(message.chat.id, "Assalomu alaykum! Quyidagi xizmatlardan birini tanlang 👇", reply_markup=kb)

# === Oddiy To'lov darrov summa kiritish ===
@bot.callback_query_handler(func=lambda c: c.data == "service:pay")
def handle_pay(call):
    msg = bot.send_message(call.message.chat.id, "Iltimos, to'lov summasini kiriting (masalan: 37000):")
    bot.register_next_step_handler(msg, process_custom_amount, "pay")

def process_custom_amount(message, service_code):
    amount_int = parse_amount(message.text)
    if amount_int is None:
        msg = bot.send_message(message.chat.id, "❌ Noto'g'ri format. Faqat raqam kiriting!")
        bot.register_next_step_handler(msg, process_custom_amount, service_code)
        return
    send_payment_info(message.chat.id, service_code, amount_int, "Custom")

# === Qolgan xizmatlar tariflari ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("service:") and c.data != "service:pay")
def handle_service(call):
    service_code = call.data.split(":")[1]
    service = SERVICES[service_code]
    kb = InlineKeyboardMarkup()
    for tariff, price in service["tariffs"].items():
        kb.add(
            InlineKeyboardButton(
                f"{tariff} - {format_amount(price)}",
                callback_data=f"tariff:{service_code}:{tariff}:{price}"
            )
        )
    kb.add(InlineKeyboardButton("💳 Oddiy To'lov", callback_data="service:pay"))
    bot.send_message(call.message.chat.id, f"{service['name']} uchun tarifni tanlang 👇", reply_markup=kb)

# === Tarif tanlandi ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("tariff:"))
def handle_tariff(call):
    _, service_code, tariff, price = call.data.split(":")
    send_payment_info(call.message.chat.id, service_code, int(price), tariff)

# === To'lov ma'lumotlari ===
def send_payment_info(chat_id, service_code, amount_int, tariff_name):
    service = SERVICES[service_code]
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Men to'lov qildim", callback_data=f"paid:{service_code}:{amount_int}:{tariff_name}"))

    text = (f"💳 {service['name']} uchun to'lov ma'lumotlari:\n\n"
            f"🔹 Tarif: {tariff_name}\n"
            f"💵 To'lanadigan summa: <b>{format_amount(amount_int)}</b>\n\n"
            f"Karta raqami: <code>{CARD_NUMBER}</code>\n"
            f"Karta egasi: {CARD_OWNER}\n\n"
            f"✅ To'lovni amalga oshirgach, pastdagi tugmani bosing yoki oxirgi 4 raqamni yuboring.")

    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)
    msg = bot.send_message(chat_id, "Iltimos, kartaning oxirgi 4 raqamini yuboring (masalan: 1234):")
    bot.register_next_step_handler(msg, process_card_last4, service_code, amount_int, tariff_name)

# === "Men to'lov qildim" ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("paid:"))
def handle_paid(call):
    _, service_code, amount_raw, tariff_name = call.data.split(":")
    amount_int = int(amount_raw)
    msg = bot.send_message(call.message.chat.id, f"{SERVICES[service_code]['name']} ({tariff_name}, {format_amount(amount_int)})\n\nIltimos kartangizning oxirgi 4 raqamini yuboring:")
    bot.register_next_step_handler(msg, process_card_last4, service_code, amount_int, tariff_name)

# === Karta oxirgi 4 ===
def process_card_last4(message, service_code, amount_int, tariff_name):
    txt = (message.text or "").strip()
    if not re.fullmatch(r"\d{4}", txt):
        msg = bot.send_message(message.chat.id, "❌ Noto'g'ri format. Faqat 4 ta raqam yuboring!")
        bot.register_next_step_handler(msg, process_card_last4, service_code, amount_int, tariff_name)
        return
    msg = bot.send_message(message.chat.id, "Endi ism va familiyangizni yuboring:")
    bot.register_next_step_handler(msg, process_fullname, txt, service_code, amount_int, tariff_name)

# === Ism Familiya ===
def process_fullname(message, card_last4, service_code, amount_int, tariff_name):
    fullname = (message.text or "").strip()
    if len(fullname) < 3:
        msg = bot.send_message(message.chat.id, "Ism va familiya juda qisqa. Qaytadan yuboring:")
        bot.register_next_step_handler(msg, process_fullname, card_last4, service_code, amount_int, tariff_name)
        return

    service = SERVICES[service_code]
    formatted_amount = format_amount(amount_int)

    bot.send_message(message.chat.id, f"✅ {service['name']} ({tariff_name}, {formatted_amount}) bo‘yicha ma'lumot qabul qilindi.")

    admin_text = (f"📩 Yangi to'lov:\n\n"
                  f"🔹 Xizmat: {service['name']}\n"
                  f"📦 Tarif: {tariff_name}\n"
                  f"💵 Summasi: {formatted_amount}\n\n"
                  f"👤 User: @{message.from_user.username or '—'} (id: {message.from_user.id})\n"
                  f"👨‍💼 Ism/Familiya: {fullname}\n"
                  f"💳 Karta (oxirgi 4): **** {card_last4}\n"
                  f"🔖 To'lov kartasi (botdagi): {CARD_NUMBER}")
    bot.send_message(ADMIN_ID, admin_text)

# === Run ===
print("🤖 Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
