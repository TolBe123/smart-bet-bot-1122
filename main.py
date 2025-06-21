
import os
import json
import matplotlib.pyplot as plt
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

BANK_FILE = "bank.txt"
PLACED_FILE = "placed.txt"
STATS_FILE = "stats.json"

def get_value_bets():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds?regions=eu&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        matches = res.json()
        results = []
        for match in matches:
            teams = match['home_team'] + " vs " + match['away_team']
            for bookmaker in match.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        name = outcome['name']
                        odds = outcome['price']
                        implied_prob = 1 / odds
                        value = round((odds * (1 - implied_prob) - 1) * 100, 2)
                        if value > 0:
                            results.append({
                                "match": teams,
                                "bet": name,
                                "odds": odds,
                                "value": value,
                                "kelly": round(value / (odds - 1), 2)
                            })
        return results[:5]
    except:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💰 Банк"), KeyboardButton("📈 График")],
        [KeyboardButton("📋 Сделано"), KeyboardButton("📊 Статистика")],
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
            f"🏟 *{b['match']}*\n"
"
            f"🎯 {b['bet']}
"
            f"📈 {b['odds']}
"
            f"📊 {b['value']}%
"
            f"🎯 Kelly: {b['kelly']}"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(BANK_FILE):
        with open(BANK_FILE, 'w') as f:
            f.write("1000")
    with open(BANK_FILE) as f:
        bank = f.read()
    await update.message.reply_text(f"*💰 Текущий банк:* {bank}₽", parse_mode=ParseMode.MARKDOWN)

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w') as f:
            json.dump([1000], f)
    with open(STATS_FILE) as f:
        data = json.load(f)
    x = list(range(len(data)))
    y = data
    plt.plot(x, y)
    plt.xlabel("Ставки")
    plt.ylabel("Банк")
    plt.title("Динамика банка")
    plt.grid(True)
    plt.savefig("graph.png")
    plt.close()
    with open("graph.png", "rb") as f:
        await update.message.reply_photo(f)

async def placed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(PLACED_FILE):
        with open(PLACED_FILE) as f:
            bets = f.read()
    else:
        bets = "Нет зафиксированных ставок."
    await update.message.reply_text(bets)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w') as f:
            json.dump([1000], f)
    with open(STATS_FILE) as f:
        data = json.load(f)
    profit = round(data[-1] - 1000, 2)
    await update.message.reply_text(f"*📊 Прибыль:* {profit}₽", parse_mode=ParseMode.MARKDOWN)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recommendations", recommendations))
    app.add_handler(CommandHandler("bank", bank))
    app.add_handler(CommandHandler("graph", graph))
    app.add_handler(CommandHandler("placed", placed))
    app.add_handler(CommandHandler("stats", stats))
    app.run_polling()

if __name__ == "__main__":
    main()
