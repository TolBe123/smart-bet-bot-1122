from telegram import Update
from telegram.ext import ContextTypes
from flashscore_ws import live_matches, format_match
import asyncio

async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(1)  # подстраховка, если WebSocket не успел стартовать

    if not live_matches:
        await update.message.reply_text("🔴 No live matches currently tracked.")
        return

    messages = []
    for match_id, data in live_matches.items():
        if "score" in data and ":" in data["score"]:
            try:
                home_goals, away_goals = map(int, data["score"].split(":"))
                if home_goals + away_goals >= 1:
                    messages.append("⚽ " + format_match(data))
            except:
                continue

    if messages:
        await update.message.reply_text("\n\n".join(messages))
    else:
        await update.message.reply_text("🟡 No high-interest live matches right now.")
