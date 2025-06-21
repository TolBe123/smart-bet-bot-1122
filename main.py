import os
import json
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = "0f3738a6d81488646926dea5b816c471"

def get_value_bets():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds?regions=eu&markets=h2h&oddsFormat=decimal&apiKey={API_KEY}"
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
        [KeyboardButton("/bank"), KeyboardButton("/graph")],
        [KeyboardButton("/placed"), KeyboardButton("/stats")],
        [KeyboardButton("/recommendations")]
    ]
    await update.message.reply_text("SmartBetAssistant Ready.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bets = get_value_bets()
    if not bets:
        await update.message.reply_text("No value bets available.")
        return
    for b in bets:
        msg = (
            f"⚽ *{b['match']}*\n"
            f"📌 Bet: *{b['bet']}*\n"
            f"💰 Odds: *{b['odds']}*\n"
            f"📈 Value: *+{b['value']}%*\n"
            f"🧮 Bet: *{b['kelly']}%* of bank"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recommendations", recommendations))
    app.run_polling()

if __name__ == "__main__":
    main()