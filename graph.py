import matplotlib.pyplot as plt
import json
import os
from telegram import Update
from telegram.ext import ContextTypes

HISTORY_FILE = "data/history.json"

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(HISTORY_FILE):
        await update.message.reply_text("No history yet.")
        return

    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)

    if not data:
        await update.message.reply_text("History is empty.")
        return

    dates = [x["date"] for x in data]
    values = [x["bank"] for x in data]

    plt.figure()
    plt.plot(dates, values, marker="o")
    plt.xticks(rotation=45)
    plt.title("Bank Over Time")
    plt.tight_layout()
    plt.savefig("bank_graph.png")
    plt.close()

    await update.message.reply_photo(photo=open("bank_graph.png", "rb"))
