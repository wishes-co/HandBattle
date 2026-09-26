import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database import (
    create_tables,
    add_player,
    get_stats,
    record_result
)

from game import (
    join_match,
    get_match,
    submit_choice
)


BOT_TOKEN = os.getenv("BOT_TOKEN")


def number_buttons(match_id):
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"play:{match_id}:1"),
            InlineKeyboardButton("2️⃣", callback_data=f"play:{match_id}:2"),
            InlineKeyboardButton("3️⃣", callback_data=f"play:{match_id}:3")
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"play:{match_id}:4"),
            InlineKeyboardButton("5️⃣", callback_data=f"play:{match_id}:5"),
            InlineKeyboardButton("6️⃣", callback_data=f"play:{match_id}:6")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def score_text(match):
    return (
        f"🏏 {match['player1']['username']}: "
        f"{match['score1']}/{match['wickets1']}\n"
        f"🏏 {match['player2']['username']}: "
        f"{match['score2']}/{match['wickets2']}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 HAND CRICKET BOT\n\n"
        "/join - Find an opponent\n"
        "/stats - View your stats"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_player(
        user.id,
        user.username or user.first_name
    )

    data = get_stats(user.id)

    if not data:
        await update.message.reply_text(
            "❌ Stats not found."
        )
        return

    username, matches, wins, losses = data

    await update.message.reply_text(
        "📊 YOUR STATS\n\n"
        f"👤 Player: {username}\n"
        f"🏏 Matches: {matches}\n"
        f"🏆 Wins: {wins}\n"
        f"❌ Losses: {losses}"
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or user.first_name

    add_player(user.id, username)

    result = join_match(user.id, username)

    if result["status"] == "waiting":
        await update.message.reply_text(
            "⏳ Waiting for another player..."
        )
        return

    if result["status"] == "already_waiting":
        await update.message.reply_text(
            "⚠️ You are already waiting."
        )
        return

    if result["status"] == "matched":

        match_id = result["match_id"]

        p1 = result["player1"]["username"]
        p2 = result["player2"]["username"]

        await update.message.reply_text(
            "🔥 MATCH FOUND!\n\n"
            f"🏏 {p1} vs {p2}\n\n"
            "Choose a number from 1–6.\n"
            "Same number = WICKET 💥\n"
            "Different number = runs.\n\n"
            "🎮 Choose your number:",
            reply_markup=number_buttons(match_id)
        )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")

    match_id = parts[1]
    choice = int(parts[2])

    match = get_match(match_id)

    if not match:
        await query.edit_message_text(
            "❌ Match not found."
        )
        return

    user_id = query.from_user.id

    players = [
        match["player1"]["user_id"],
        match["player2"]["user_id"]
    ]

    if user_id not in players:
        await query.answer(
            "You are not part of this match!",
            show_alert=True
        )
        return

    if user_id in match["choices"]:
        await query.answer(
            "You already selected!",
            show_alert=True
        )
        return

    result = submit_choice(
        match_id,
        user_id,
        choice
    )

    if result["status"] == "waiting":
        await query.edit_message_text(
            "✅ Your number is locked!\n\n"
            "⏳ Waiting for your opponent..."
        )
        return

    if result["status"] == "innings_end":

        await query.edit_message_text(
            "🔄 INNINGS OVER!\n\n"
            f"{score_text(match)}\n\n"
            f"🎯 Target: {result['target']}\n\n"
            "🏏 Second innings begins!",
            reply_markup=number_buttons(match_id)
        )
        return

    if result["status"] == "match_end":

        score1 = result["score1"]
        score2 = result["score2"]

        if score1 > score2:
            winner_id = match["player1"]["user_id"]
            loser_id = match["player2"]["user_id"]
            winner = match["player1"]["username"]

        elif score2 > score1:
            winner_id = match["player2"]["user_id"]
            loser_id = match["player1"]["user_id"]
            winner = match["player2"]["username"]

        else:
            await query.edit_message_text(
                "🤝 MATCH DRAW!\n\n"
                f"{score_text(match)}"
            )
            return

        record_result(
            winner_id,
            loser_id
        )

        await query.edit_message_text(
            "🏆 MATCH OVER!\n\n"
            f"🥇 Winner: {winner}\n\n"
            f"{score_text(match)}\n\n"
            "📊 Use /stats to check your record."
        )
        return

    if result["status"] == "wicket":

        await query.edit_message_text(
            "💥 WICKET!\n\n"
            f"Both chose {result['choice1']}.\n\n"
            f"{score_text(match)}\n\n"
            "🎮 Next ball:",
            reply_markup=number_buttons(match_id)
        )
        return

    if result["status"] == "runs":

        await query.edit_message_text(
            f"🏏 {result['runs']} RUNS!\n\n"
            f"{score_text(match)}\n\n"
            "🎮 Next ball:",
            reply_markup=number_buttons(match_id)
        )


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("join", join)
    )

    app.add_handler(
        CommandHandler("stats", stats)
    )

    app.add_handler(
        CallbackQueryHandler(
            play,
            pattern=r"^play:"
        )
    )

    print("🏏 Hand Cricket Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
