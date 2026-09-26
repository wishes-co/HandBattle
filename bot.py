import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from database import create_tables, add_player


BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 Welcome to Hand Cricket Bot!\n\n"
        "Commands:\n"
        "/join - Join the game\n"
        "/start - Start the bot"
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_player(
        user.id,
        user.username or user.first_name
    )

    await update.message.reply_text(
        f"🏏 {user.first_name} joined Hand Cricket!\n\n"
        "Waiting for another player..."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))

    print("🏏 Hand Cricket Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
