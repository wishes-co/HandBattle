import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 Welcome to Hand Cricket Bot!\n\n"
        "Use /join to join a match."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🏏 Hand Cricket Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
