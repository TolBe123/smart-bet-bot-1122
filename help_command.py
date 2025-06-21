from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/recommendations - Get value bets
"
        "/bank - Show current bank
"
        "/placed - List placed bets
"
        "/graph - Show bank graph
"
        "/stats - Show performance stats"
    )
