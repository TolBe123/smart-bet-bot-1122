import json, os
from telegram import Update
from telegram.ext import ContextTypes

HISTORY_FILE = "data/history.json"

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(HISTORY_FILE):
        await update.message.reply_text("No history available.")
        return

    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)

    if len(data) < 2:
        await update.message.reply_text("Not enough data.")
        return

    start = data[0]["bank"]
    end = data[-1]["bank"]
    change = end - start
    roi = (change / start) * 100

    await update.message.reply_text(f"📈 Start: {start:.2f}₽
💰 Now: {end:.2f}₽
📊 ROI: {roi:.2f}%")
