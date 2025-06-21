import os
import json
import matplotlib.pyplot as plt
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from betting import get_value_bets

BANK_FILE = "bank.txt"
STATS_FILE = "stats.json"
PLACED_FILE = "placed.txt"

def init_files():
    if not os.path.exists(BANK_FILE):
        with open(BANK_FILE, "w") as f:
            f.write("1000")
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump([1000], f)
    if not os.path.exists(PLACED_FILE):
        with open(PLACED_FILE, "w") as f:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💰 Банк"), KeyboardButton("📝 График")],
        [KeyboardButton("✅ Сделано"), KeyboardButton("📈 Статистика")],
        [KeyboardButton("📌 Ставки")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("SmartBetAssistant Ready.", reply_markup=reply_markup)

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bets = get_value_bets()
    if not bets:
        await update.message.reply_text("No value bets available.")
        return
    for b in bets:
        msg = (
            f"*🏟 {b['match']}*\n"
            f"🎯 {b['bet']}\n"
            f"📈 {b['odds']}\n"
            f"📊 {b['value']}%\n"
            f"🎯 Kelly: {b['kelly']}"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        with open(PLACED_FILE, "a") as f:
            f.write(json.dumps(b) + "\n")

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(BANK_FILE) as f:
        bank = f.read()
    await update.message.reply_text(f"*💰 Текущий банк:* {bank}", parse_mode=ParseMode.MARKDOWN)

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(STATS_FILE) as f:
        data = json.load(f)
    x = list(range(len(data)))
    y = data
    plt.plot(x, y)
    plt.xlabel("Ставки")
    plt.ylabel("Банк")
    plt.title("История банка")
    plt.savefig("bank_graph.png")
    plt.close()
    await update.message.reply_photo(photo=open("bank_graph.png", "rb"))

async def placed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PLACED_FILE):
        await update.message.reply_text("Нет сделанных ставок.")
        return
    with open(PLACED_FILE) as f:
        lines = f.readlines()[-5:]
    if not lines:
        await update.message.reply_text("Нет сделанных ставок.")
        return
    for line in lines:
        try:
            b = json.loads(line.strip())
            msg = (
                f"*🏟 {b['match']}*\n"
                f"🎯 {b['bet']}\n"
                f"📈 {b['odds']}\n"
                f"📊 {b['value']}%\n"
                f"🎯 Kelly: {b['kelly']}"
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        except:
            continue

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(STATS_FILE) as f:
        data = json.load(f)
    change = round(data[-1] - data[0], 2)
    await update.message.reply_text(f"📈 Прибыль: {change}", parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    init_files()
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recommendations", recommendations))
    app.add_handler(CommandHandler("bank", bank))
    app.add_handler(CommandHandler("graph", graph))
    app.add_handler(CommandHandler("placed", placed))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Regex("💰 Банк"), bank))
    app.add_handler(MessageHandler(filters.Regex("📝 График"), graph))
    app.add_handler(MessageHandler(filters.Regex("✅ Сделано"), placed))
    app.add_handler(MessageHandler(filters.Regex("📈 Статистика"), stats))
    app.add_handler(MessageHandler(filters.Regex("📌 Ставки"), recommendations))
    app.run_polling()
