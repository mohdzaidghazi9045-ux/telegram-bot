import telebot
from telebot import types
import qrcode

# ========= CONFIG =========

TOKEN = "8273870987:AAHaMJfCgmowIFVKmoZWhCrBc50rVC3yG74"

ADMIN_ID = 8578580859

USDT_ADDRESS = "TFybYDjYV5zquis8zxKbZLit1MxJ5b3Xbk"

CHANNEL_LINK = "https://t.me/+Sgbibuk4vDIyNjJl"

# ==========================

bot = telebot.TeleBot(TOKEN)

# ===== CREATE QR =====

qr = qrcode.make(USDT_ADDRESS)
qr.save("qr.png")

# ===== START =====

@bot.message_handler(commands=['start'])
def start(message):

    text = """
📚 Welcome!

Get access to premium study resources, notes and private discussions.

Press Continue to proceed.
"""

    markup = types.InlineKeyboardMarkup()

    continue_btn = types.InlineKeyboardButton(
        "Continue ✅",
        callback_data="continue"
    )

    cancel_btn = types.InlineKeyboardButton(
        "Cancel ❌",
        callback_data="cancel"
    )

    markup.add(continue_btn)
    markup.add(cancel_btn)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

# ===== BUTTONS =====

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    # CONTINUE
    if call.data == "continue":

        terms = """
📜 TERMS & CONDITIONS

• Payment verification may take a few minutes.
• Send screenshot after payment.
• Keep your Telegram username visible.
• Access will be provided after approval.
"""

        markup = types.InlineKeyboardMarkup()

        agree_btn = types.InlineKeyboardButton(
            "Agree ✅",
            callback_data="agree"
        )

        reject_btn = types.InlineKeyboardButton(
            "Reject ❌",
            callback_data="reject_terms"
        )

        markup.add(agree_btn)
        markup.add(reject_btn)

        bot.edit_message_text(
            terms,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    # CANCEL
    elif call.data == "cancel":

        bot.edit_message_text(
            "Request cancelled.",
            call.message.chat.id,
            call.message.message_id
        )

    # AGREE
    elif call.data == "agree":

        caption = f"""
💳 PAYMENT DETAILS

Send exactly $15 USDT

📮 USDT Address:

{USDT_ADDRESS}

⚠️ After payment send screenshot in this bot.
"""

        with open("qr.png", "rb") as photo:

            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=caption
            )

    # REJECT TERMS
    elif call.data == "reject_terms":

        bot.edit_message_text(
            "You rejected the terms.",
            call.message.chat.id,
            call.message.message_id
        )

    # ADMIN APPROVE
    elif call.data.startswith("approve_"):

        user_id = call.data.split("_")[1]

        bot.send_message(
            user_id,
            f"""
✅ PAYMENT VERIFIED

Private Access Link 👇

{CHANNEL_LINK}
"""
        )

        bot.answer_callback_query(
            call.id,
            "User approved"
        )

    # ADMIN REJECT
    elif call.data.startswith("reject_"):

        user_id = call.data.split("_")[1]

        bot.send_message(
            user_id,
            "❌ Verification failed.\nPlease send a clearer screenshot."
        )

        bot.answer_callback_query(
            call.id,
            "User rejected"
        )

# ===== RECEIVE SCREENSHOT =====

@bot.message_handler(content_types=['photo'])
def receive_photo(message):

    username = message.from_user.username

    if username is None:
        username = "No Username"

    caption = f"""
📥 PAYMENT SCREENSHOT

👤 Name: {message.from_user.first_name}

🔗 Username: @{username}

🆔 User ID: {message.from_user.id}
"""

    file_id = message.photo[-1].file_id

    # SEND TO ADMIN

    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=caption
    )

    # ADMIN ACTION BUTTONS

    markup = types.InlineKeyboardMarkup()

    approve_btn = types.InlineKeyboardButton(
        "Approve ✅",
        callback_data=f"approve_{message.chat.id}"
    )

    reject_btn = types.InlineKeyboardButton(
        "Reject ❌",
        callback_data=f"reject_{message.chat.id}"
    )

    markup.add(approve_btn)
    markup.add(reject_btn)

    bot.send_message(
        ADMIN_ID,
        "Choose action:",
        reply_markup=markup
    )

    # USER MESSAGE

    bot.reply_to(
        message,
        "✅ Screenshot received.\nPlease wait for verification."
    )

# ===== RUN =====

print("BOT RUNNING...")

bot.infinity_polling(skip_pending=True)