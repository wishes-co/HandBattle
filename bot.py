import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from database import create_tables, add_player
from game import join_match, toss


BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 Welcome to Hand Cricket!\n\n"
        "Use /join to find an opponent."
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or user.first_name

    add_player(user.id, username)

    result = join_match(user.id, username)

    if result["status"] == "waiting":
        await update.message.reply_text(
            "⏳ You joined the queue!\n"
            "Waiting for another player..."
        )

    elif result["status"] == "already_waiting":
        await update.message.reply_text(
            "⚠️ You are already waiting for an opponent."
        )

    elif result["status"] == "matched":
        player1 = result["player1"]["username"]
        player2 = result["player2"]["username"]

        batting = toss()

        if batting == "player1":
            first_batter = player1
        else:
            first_batter = player2

        await update.message.reply_text(
            "🔥 MATCH FOUND!\n\n"
            f"🏏 {player1} vs {player2}\n\n"
            f"🪙 Toss result:\n"
            f"🏏 {first_batter} bats first!\n\n"
            "Game is ready!"
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
