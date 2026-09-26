import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database import create_tables, add_player
from game import join_match, get_match, play_ball


BOT_TOKEN = os.getenv("BOT_TOKEN")


def number_buttons(match_id):
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"play:{match_id}:1"),
            InlineKeyboardButton("2️⃣", callback_data=f"play:{match_id}:2"),
            InlineKeyboardButton("3️⃣", callback_data=f"play:{match_id}:3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"play:{match_id}:4"),
            InlineKeyboardButton("5️⃣", callback_data=f"play:{match_id}:5"),
            InlineKeyboardButton("6️⃣", callback_data=f"play:{match_id}:6"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


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
        return

    if result["status"] == "already_waiting":
        await update.message.reply_text(
            "⚠️ You are already waiting."
        )
        return

    if result["status"] == "matched":
        match_id = result["match_id"]
        player1 = result["player1"]["username"]
        player2 = result["player2"]["username"]

        await update.message.reply_text(
            "🔥 MATCH FOUND!\n\n"
            f"🏏 {player1} vs {player2}\n\n"
            "Choose your number from 1 to 6.\n"
            "The same number means WICKET! 💥",
            reply_markup=number_buttons(match_id)
        )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")

    match_id = parts[1]
    player_number = int(parts[2])

    match = get_match(match_id)

    if not match:
        await query.edit_message_text("❌ Match not found.")
        return

    # Simple demo opponent choice
    opponent_number = __import__("random").randint(1, 6)

    result = play_ball(
        match_id,
        player_number,
        opponent_number
    )

    if result["result"] == "wicket":
        message = (
            f"💥 WICKET!\n\n"
            f"You chose: {player_number}\n"
            f"Opponent chose: {opponent_number}\n\n"
            "Same number!"
        )
    else:
        message = (
            f"🏏 {result['runs']} RUNS!\n\n"
            f"You chose: {player_number}\n"
            f"Opponent chose: {opponent_number}\n\n"
            f"Score: {result['runs']}"
        )

    await query.edit_message_text(
        message,
        reply_markup=number_buttons(match_id)
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CallbackQueryHandler(play, pattern=r"^play:"))

    print("🏏 Hand Cricket Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
