import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import logging

# === Sozlamalar ===
BOT_TOKEN = "8114837659:AAHYY_MbvGE2J_ps7M98MmYVljBCNJavGVE"
ADMIN_ID = 6234736126
CHANNEL_USERNAME = "premum_uc_hizmati"  # @ belgisisiz
CARD_NUMBER = "9860 1678 2074 3752"
CARD_OWNER = "I. TORAXON"

# === Log ===
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)

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

# === Foydali funksiya ===
def format_amount(amount_int):
    return f"{amount_int:,}".replace(",", " ") + " so'm"

# === Kanal obuna tekshiruvi ===
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# === Start buyrug‘i ===
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # Avval hush kelibsiz
    bot.send_message(
        message.chat.id,
        "👋 <b>Assalomu alaykum!</b>\nPremium botga va boshqa xizmatlarga xush kelibsiz!",
        parse_mode="HTML"
    )

    # Keyin obuna tekshirish
    if not check_subscription(user_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME}"))
        kb.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
        bot.send_message(
            message.chat.id,
            f"📢 Botdan foydalanish uchun avval kanalga obuna bo‘ling:\n👉 @{CHANNEL_USERNAME}",
            reply_markup=kb
        )
        return

    # Agar obuna bo‘lgan bo‘lsa
    show_services_menu(message.chat.id)

# === Obuna qayta tekshirish ===
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def recheck_subscription(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_services_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!")

# === Xizmatlar menyusi ===
def show_services_menu(chat_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⭐ Telegram Premium", callback_data="service:premium"))
    kb.add(InlineKeyboardButton("✨ Telegram Stars", callback_data="service:stars"))
    kb.add(InlineKeyboardButton("💎 Mobile Legends", callback_data="service:mlbb"))
    kb.add(InlineKeyboardButton("🎮 PUBG UC", callback_data="service:uc"))

    text = (
        "🤖 <b>Premium xizmatlar menyusi:</b>\n"
        "Quyidagi xizmatlardan birini tanlang 👇"
    )
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)

# === Xizmat tanlash ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("service:"))
def handle_service(call):
    service_code = call.data.split(":")[1]
    service = SERVICES[service_code]

    kb = InlineKeyboardMarkup()
    for tariff, price in service["tariffs"].items():
        kb.add(InlineKeyboardButton(f"{tariff} - {format_amount(price)}", callback_data=f"tariff:{service_code}:{tariff}:{price}"))

    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📦 <b>{service['name']}</b>\nKerakli tarifni tanlang 👇",
        parse_mode="HTML",
        reply_markup=kb
    )

# === Tarif tanlangandan so‘ng to‘lov ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("tariff:"))
def handle_tariff(call):
    _, service_code, tariff_name, price = call.data.split(":")
    user_id = call.from_user.id

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💳 To‘lov qildim", callback_data=f"paid:{service_code}:{tariff_name}:{price}"))
    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu"))

    text = (
        f"💰 <b>To‘lov ma’lumotlari</b>\n\n"
        f"📦 Xizmat: <b>{SERVICES[service_code]['name']}</b>\n"
        f"📅 Tarif: <b>{tariff_name}</b>\n"
        f"💵 Narx: <b>{format_amount(int(price))}</b>\n\n"
        f"💳 To‘lov kartasi:\n<b>{CARD_NUMBER}</b>\n<b>{CARD_OWNER}</b>\n\n"
        f"To‘lovni amalga oshirgach, «💳 To‘lov qildim» tugmasini bosing."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=kb
    )

# === To‘lov qildim tugmasi ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("paid:"))
def handle_paid(call):
    _, service_code, tariff_name, price = call.data.split(":")
    user_id = call.from_user.id

    bot.send_message(
        call.message.chat.id,
        "📸 Endi to‘lov chekingizni yuboring (rasm shaklida)."
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: receive_check(msg, service_code, tariff_name, price)
    )

# === Chek qabul qilish ===
def receive_check(message, service_code, tariff_name, price):
    if not message.photo:
        bot.send_message(message.chat.id, "❗ Iltimos, chekni rasm shaklida yuboring.")
        return

    photo_id = message.photo[-1].file_id

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Chekni yubordim", callback_data=f"checksent:{service_code}:{tariff_name}:{price}:{photo_id}"))

    bot.send_message(message.chat.id, "✅ Agar chek to‘liq yuklangan bo‘lsa, pastdagi tugmani bosing:", reply_markup=kb)

# === Chek yuborildi ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("checksent:"))
def handle_check_sent(call):
    _, service_code, tariff_name, price, photo_id = call.data.split(":")
    user = call.from_user

    # Admin uchun xabar
    caption = (
        f"📥 <b>Yangi to‘lov!</b>\n\n"
        f"👤 Ism: <b>{user.first_name}</b>\n"
        f"🔗 Username: @{user.username if user.username else 'yo‘q'}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"📦 Xizmat: <b>{SERVICES[service_code]['name']}</b>\n"
        f"📅 Tarif: <b>{tariff_name}</b>\n"
        f"💵 Narx: <b>{format_amount(int(price))}</b>"
    )

    bot.send_photo(ADMIN_ID, photo=photo_id, caption=caption, parse_mode="HTML")
    bot.send_message(call.message.chat.id, "✅ Chek yuborildi! Admin tekshirib beradi.")
    bot.answer_callback_query(call.id, "✅ Chek yuborildi!")

# === Orqaga menyu ===
@bot.callback_query_handler(func=lambda c: c.data == "back_to_menu")
def back_to_menu(call):
    show_services_menu(call.message.chat.id)

# === Ishga tushirish ===
print("✅ Bot ishga tushdi...")
bot.infinity_polling()
