import os
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

API_KEY = os.getenv("API_FOOTBALL_KEY")

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "x-apisports-key": API_KEY
    }

    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={today}&timezone=Europe/Moscow"

    try:
        response = requests.get(url, headers=headers)
        data = response.json().get("response", [])

        await update.message.reply_text(f"📅 Найдено матчей: {len(data)}")

        if not data:
            await update.message.reply_text("⚠️ Нет матчей на сегодня.")
            return

        # Покажем первые 3 матча (как тест)
        for match in data[:3]:
            league = match["league"]["name"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            time = match["fixture"]["date"][11:16]

            await update.message.reply_text(
                f"🏆 {league}\n"
                f"⚽ {home} vs {away}\n"
                f"🕒 Время: {time} (по МСК)"
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
