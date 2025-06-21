from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/recommendations - Get value bets\n"
        "/bank - Show current bank\n"
        "/placed - List placed bets\n"
        "/graph - Show bank graph\n"
        "/stats - Show performance stats"
    )
