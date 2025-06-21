from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    f"📈 Start: {start:.2f}₽\n"
    f"💰 Now: {end:.2f}₽\n"
    f"📊 ROI: {roi:.2f}%"
    )
