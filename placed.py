import json, os
from telegram import Update
from telegram.ext import ContextTypes

PLACED_FILE = "data/placed.json"

async def placed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PLACED_FILE):
        await update.message.reply_text("No bets placed yet.")
        return

    with open(PLACED_FILE, "r") as f:
        data = json.load(f)
    if not data:
        await update.message.reply_text("No bets placed.")
        return

    messages = [f"{i+1}) {b['match']} — {b['bet']} @ {b['odd']} ({b['stake']}₽)" for i, b in enumerate(data[-5:])]
    await update.message.reply_text("📌 Recent bets:
" + "
".join(messages))
