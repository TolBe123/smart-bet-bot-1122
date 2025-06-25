from telegram import Update
from telegram.ext import ContextTypes
from recommendations import fetch_live_value_bets
import asyncio

async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Live value betting started...")

    async def send_value(event, outcome, odd, value):
        text = f"📊 Value bet found:\n" \
               f"🏟 {event.get('name', 'Unknown')}\n" \
               f"🧾 Outcome: {outcome.get('name', 'N/A')}\n" \
               f"💸 Odd: {odd}\n" \
               f"📈 Value: {round(value * 100, 2)}%"
        await update.message.reply_text(text)

    asyncio.create_task(fetch_live_value_bets(send_value))