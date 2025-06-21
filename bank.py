import json
from telegram import Update
from telegram.ext import ContextTypes
import os

BANK_FILE = "data/bank.json"

def read_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r") as f:
            return float(f.read())
    return 1000.0

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bank_value = read_bank()
    await update.message.reply_text(f"Current bank: {bank_value:.2f}₽")
