import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

# === Sozlamalar ===
BOT_TOKEN = "8114837659:XXXXXXXXXXXX"  # <-- Tokenni bu yerga yozing
ADMIN_ID = 6234736126
CARD_NUMBER = "9860 1678 2074 3752"
CARD_OWNER = "I. TORAXON"

# === Majburiy kanal ===
CHANNELS = ["@premum_uc_hizmati"]

# === Xizmatlar ===
SERVICES = {
    "premium": {
        "name": "👑 Telegram Premium",
        "tariffs": {
            "1 oy": 52000,
            "3 oy": 200000,
            "12 oy": 400000
        }
    },
    "stars": {
        "name": "✨ Telegram Stars",
        "tariffs": {
            "100⭐": 26000,
            "250⭐": 60000,
            "1000⭐": 240000
        }
    },
    "mlbb": {
        "name": "💎 Mobile Legends",
        "tariffs": {
            "86💎": 25000,
            "172💎": 47000,
            "257💎": 70000,
            "514💎": 135000,
            "1000💎": 260000
        }
    },
    "uc": {
        "name": "🎮 PUBG UC",
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

# === Obuna tekshirish ===
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ["member", "creator", "administrator"]:
                return False
        except:
            return False
    return True

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id):
        send_subscribe_message(message.chat.id)
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("👑 Telegram Premium", callback_data="service:premium"))
    kb.add(InlineKeyboardButton("✨ Telegram Stars", callback_data="service:stars"))
    kb.add(InlineKeyboardButton("💎 Mobile Legends", callback_data="service:mlbb"))
    kb.add(InlineKeyboardButton("🎮 PUBG UC", callback_data="service:uc"))

    text = (
        "👋 <b>Assalomu alaykum!</b>\n"
        "🤖 Botimizga <b>xush kelibsiz!</b>\n\n"
        "Quyidagi xizmatlardan birini tanlang 👇"
    )

    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=kb)

# === Obuna xabari ===
def send_subscribe_message(chat_id):
    kb = InlineKeyboardMarkup()
    for ch in CHANNELS:
        kb.add(InlineKeyboardButton("📢 Kanalga o‘tish", url=f"https://t.me/{ch.replace('@', '')}"))
    kb.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
    bot.send_message(chat_id,
                     "🔔 Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling 👇",
                     reply_markup=kb)

# === Obunani tekshirish ===
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(call):
    if check_subscription(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!", show_alert=True)

# === Oddiy to‘lov ===
@bot.callback_query_handler(func=lambda c: c.data == "service:pay")
def handle_pay(call):
    msg = bot.send_message(call.message.chat.id, "💵 Iltimos, to‘lov summasini kiriting (masalan: 37000):")
    bot.register_next_step_handler(msg, process_custom_amount, "pay")

def process_custom_amount(message, service_code):
    amount_int = parse_amount(message.text)
    if amount_int is None:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri format. Faqat raqam kiriting!")
        bot.register_next_step_handler(msg, process_custom_amount, service_code)
        return
    send_payment_info(message.chat.id, service_code, amount_int, "Custom")

# === Xizmatlar menyusi ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("service:") and c.data != "service:pay")
def handle_service(call):
    service_code = call.data.split(":")[1]
    service = SERVICES[service_code]
    kb = InlineKeyboardMarkup()
    for tariff, price in service["tariffs"].items():
        kb.add(InlineKeyboardButton(f"{tariff} • {format_amount(price)}",
                                    callback_data=f"tariff:{service_code}:{tariff}:{price}"))
    kb.add(InlineKeyboardButton("💳 Oddiy To‘lov", callback_data="service:pay"))
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
    text = (f"💳 <b>{service['name']}</b> uchun to‘lov ma’lumotlari:\n\n"
            f"📦 Tarif: <b>{tariff_name}</b>\n"
            f"💰 Summa: <b>{format_amount(amount_int)}</b>\n\n"
            f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
            f"👤 Karta egasi: <b>{CARD_OWNER}</b>\n\n"
            f"✅ To‘lovni amalga oshirgach, pastdagi tugmani bosing.")
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)

# === "Men to‘lov qildim" ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("paid:"))
def handle_paid(call):
    _, service_code, amount_raw, tariff_name = call.data.split(":")
    amount_int = int(amount_raw)
    msg = bot.send_message(call.message.chat.id, "📸 Iltimos, to‘lov chekini (rasmni) yuboring:")
    bot.register_next_step_handler(msg, process_receipt, service_code, amount_int, tariff_name)

# === Chek yuborish ===
def process_receipt(message, service_code, amount_int, tariff_name):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❌ Chek rasm yuboring. Qaytadan urinib ko‘ring:")
        bot.register_next_step_handler(msg, process_receipt, service_code, amount_int, tariff_name)
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Chekni yubordim", callback_data=f"confirm:{service_code}:{amount_int}:{tariff_name}"))
    bot.send_message(message.chat.id, "✅ Chek qabul qilindi!\nAgar to‘liq yuborgan bo‘lsangiz, pastdagi tugmani bosing 👇", reply_markup=kb)

    # Admin’ga chek yuborish
    file_id = message.photo[-1].file_id
    service = SERVICES[service_code]
    formatted_amount = format_amount(amount_int)
    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=(f"📩 <b>Yangi to‘lov</b>\n\n"
                 f"🔹 Xizmat: {service['name']}\n"
                 f"📦 Tarif: {tariff_name}\n"
                 f"💵 Summasi: {formatted_amount}\n\n"
                 f"👤 User: @{message.from_user.username or '—'}\n"
                 f"🆔 ID: {message.from_user.id}"),
        parse_mode="HTML"
    )

# === Chekni yubordim ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm:"))
def handle_confirm(call):
    bot.send_message(call.message.chat.id, "✅ Rahmat! Chekingiz adminga yuborildi.\n⏳ Tez orada siz bilan bog‘lanishadi.")

# === Run ===
print("🤖 Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
