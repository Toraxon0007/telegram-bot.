import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# === Sozlamalar ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # <-- Bot tokeningizni shu joyga yozing
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


def format_amount(amount_int):
    return f"{amount_int:,}".replace(",", " ") + " so'm"


def check_subscription(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# === /start komandasi ===
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        "👋 <b>Assalomu alaykum!</b>\nPremium botga va boshqa xizmatlarga xush kelibsiz!",
        parse_mode="HTML"
    )

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

    show_services_menu(message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def recheck_subscription(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_services_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!")


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


@bot.callback_query_handler(func=lambda c: c.data.startswith("service:"))
def handle_service(call):
    service_code = call.data.split(":")[1]
    service = SERVICES[service_code]

    kb = InlineKeyboardMarkup()
    for tariff, price in service["tariffs"].items():
        kb.add(InlineKeyboardButton(f"{tariff} - {format_amount(price)}",
                                    callback_data=f"tariff:{service_code}:{tariff}:{price}"))
    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📦 <b>{service['name']}</b>\nKerakli tarifni tanlang 👇",
        parse_mode="HTML",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("tariff:"))
def handle_tariff(call):
    _, service_code, tariff_name, price = call.data.split(":")
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


@bot.callback_query_handler(func=lambda c: c.data.startswith("paid:"))
def handle_paid(call):
    _, service_code, tariff_name, price = call.data.split(":")
    bot.send_message(
        call.message.chat.id,
        "📸 Endi to‘lov chekingizni yuboring (rasm shaklida)."
    )
    bot.register_next_step_handler(
        call.message,
        lambda msg: receive_check(msg, service_code, tariff_name, price)
    )


def receive_check(message, service_code, tariff_name, price):
    if not message.photo:
        bot.send_message(message.chat.id, "❗ Iltimos, chekni rasm shaklida yuboring.")
        return

    photo_id = message.photo[-1].file_id

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Chekni tashladim",
                                callback_data=f"checksent:{service_code}:{tariff_name}:{price}:{photo_id}"))

    bot.send_message(
        message.chat.id,
        "✅ Agar chek to‘liq yuklangan bo‘lsa, pastdagi tugmani bosing 👇",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("checksent:"))
def handle_check_sent(call):
    _, service_code, tariff_name, price, photo_id = call.data.split(":")
    user = call.from_user

    caption = (
        f"📥 <b>Yangi to‘lov arizasi!</b>\n\n"
        f"👤 <b>Ism:</b> {user.first_name or 'Noma’lum'}\n"
        f"🔗 <b>Username:</b> @{user.username if user.username else 'yo‘q'}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"📦 <b>Xizmat:</b> {SERVICES[service_code]['name']}\n"
        f"📅 <b>Tarif:</b> {tariff_name}\n"
        f"💵 <b>Narx:</b> {format_amount(int(price))}\n\n"
        f"📸 <b>Chek rasmi pastda:</b>"
    )

    admin_kb = InlineKeyboardMarkup()
    admin_kb.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve:{user.id}:{service_code}:{tariff_name}:{price}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user.id}:{service_code}:{tariff_name}:{price}")
    )

    bot.send_photo(ADMIN_ID, photo=photo_id, caption=caption, parse_mode="HTML", reply_markup=admin_kb)
    bot.send_message(call.message.chat.id, "✅ Chek yuborildi! Admin tez orada tekshiradi.")
    bot.answer_callback_query(call.id, "✅ Chek yuborildi!")


# === ADMIN QARORI ===
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve:") or c.data.startswith("reject:"))
def admin_decision(call):
    action, user_id, service_code, tariff_name, price = call.data.split(":")
    user_id = int(user_id)

    if action == "approve":
        # ✅ Admin tasdiqladi — foydalanuvchiga xizmat bajarilgan deb yuboriladi
        bot.send_message(
            user_id,
            f"✅ <b>Xizmat bajarildi!</b>\nSizning to‘lovingiz tasdiqlandi va xizmat yakunlandi.\n\n"
            f"📦 Xizmat: {SERVICES[service_code]['name']}\n"
            f"📅 Tarif: {tariff_name}\n"
            f"💵 Narx: {format_amount(int(price))}\n\n"
            f"🙏 Rahmat ishonchingiz uchun!",
            parse_mode="HTML"
        )

        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=f"✅ <b>To‘lov tasdiqlandi va xizmat bajarildi.</b>\n{call.message.caption}",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")

    else:
        # ❌ Admin rad etdi
        bot.send_message(
            user_id,
            f"❌ <b>To‘lov rad etildi.</b>\nIltimos, to‘lov ma’lumotlarini qayta tekshirib, to‘g‘ri chek yuboring.",
            parse_mode="HTML"
        )
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=f"❌ <b>To‘lov rad etildi.</b>\n{call.message.caption}",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, "❌ Rad etildi!")


@bot.callback_query_handler(func=lambda c: c.data == "back_to_menu")
def back_to_menu(call):
    show_services_menu(call.message.chat.id)


print("✅ Bot ishga tushdi...")
bot.infinity_polling()
