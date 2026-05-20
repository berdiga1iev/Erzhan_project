import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langdetect import detect
from deep_translator import GoogleTranslator
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# 1. Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
DB_NAME = "bot_data.db"


# 2. Database initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time TEXT,
            source_lang TEXT,
            target_lang TEXT,
            original_text TEXT,
            translated_text TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_history(user_id, original, translated, src, target):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (
            user_id,
            time,
            source_lang,
            target_lang,
            original_text,
            translated_text
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        src,
        target,
        original,
        translated
    ))

    conn.commit()
    conn.close()


# 3. Keyboards (User Interface)
def get_main_menu():
    """Main menu keyboard"""
    keyboard = [
        [KeyboardButton("📜 History"), KeyboardButton("📊 Statistics")],
        [KeyboardButton("❓ Help"), KeyboardButton("📘 About Project")],
        [KeyboardButton("🗑 Clear History")]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_lang_keyboard():
    """Inline buttons for language selection"""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="en"),
            InlineKeyboardButton("🇷🇺 Russian", callback_data="ru")
        ],
        [
            InlineKeyboardButton("🇰🇿 Kazakh", callback_data="kk"),
            InlineKeyboardButton("🇫🇷 French", callback_data="fr")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# 4. Commands
async def post_init(application):
    """Set bot commands in Telegram menu"""

    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("history", "View translation history"),
        BotCommand("stats", "Usage statistics"),
        BotCommand("clear", "Delete history"),
        BotCommand("help", "Help"),
        BotCommand("about", "About developer"),
    ]

    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello! I am a professional translator bot.\n"
        "Send me any text and I will translate it.",
        reply_markup=get_main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Available features:\n"
        "• Send any text for translation\n"
        "• 'History' button - last 5 translations\n"
        "• 'Statistics' button - total number of translations\n"
        "• 'About Project' button - developer information",
        reply_markup=get_main_menu()
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Project: Translator Chat Bot\n"
        "Subject: 'Python Programming'\n"
        "Author: Yerzhan Berdigali.",
        reply_markup=get_main_menu()
    )


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT original_text, translated_text
        FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (update.message.from_user.id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return await update.message.reply_text("📭 Your history is empty.")

    msg = "📜 Recent translations:\n\n"

    for orig, trans in rows:
        msg += f"🔹 {orig[:30]}... ➡ {trans[:30]}...\n"

    await update.message.reply_text(msg)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM history
        WHERE user_id = ?
    """, (update.message.from_user.id,))

    total = cursor.fetchone()[0]
    conn.close()

    await update.message.reply_text(
        f"📊 Total translations made: {total}"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM history
        WHERE user_id = ?
    """, (update.message.from_user.id,))

    conn.commit()
    conn.close()

    await update.message.reply_text("🗑 Your history has been cleared.")


# 5. Text and error handling
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Main menu button handling
    if user_text == "📜 History":
        return await history(update, context)

    elif user_text == "📊 Statistics":
        return await stats(update, context)

    elif user_text == "❓ Help":
        return await help_command(update, context)

    elif user_text == "📘 About Project":
        return await about(update, context)

    elif user_text == "🗑 Clear History":
        return await clear(update, context)

    # Translation logic
    if not user_text or len(user_text.strip()) == 0:
        return await update.message.reply_text(
            "❌ Error: Please enter text for translation."
        )

    greetings = ["hello", "hi", "hey", "salem"]

    if user_text.lower() in greetings:
        return await update.message.reply_text(
            "👋 Hello! I am ready to translate. Just send me a text."
        )

    context.user_data["text"] = user_text

    await update.message.reply_text(
        "🌍 Choose the target language:",
        reply_markup=get_lang_keyboard()
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = context.user_data.get("text")

    if not text:
        return await query.edit_message_text(
            "❌ Context lost. Please enter the text again."
        )

    try:
        source_lang = detect(text)
        target_lang = query.data

        translated = GoogleTranslator(
            source="auto",
            target=target_lang
        ).translate(text)

        add_history(
            query.from_user.id,
            text,
            translated,
            source_lang,
            target_lang
        )

        await query.edit_message_text(
            f"✅ Result:\n\n"
            f"{translated}\n\n"
            f"🌐 {source_lang} → {target_lang}"
        )

    except Exception:
        await query.edit_message_text(
            "❌ Translation error. Please try another phrase."
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤔 I don't understand this command. Use the menu or /help."
    )


# 6. Main function
def main():
    init_db()

    # Added post_init for command menu creation
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("about", about))

    # Message handlers
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    app.add_handler(CallbackQueryHandler(handle_button))

    # Unknown command handler
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🤖 Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()