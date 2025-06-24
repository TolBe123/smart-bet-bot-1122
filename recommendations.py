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

    # Текущая дата
    today = datetime.today().strftime('%Y-%m-%d')
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?date={today}"

    try:
        # Получаем список матчей
        resp = requests.get(fixtures_url, headers=headers)
        resp.raise_for_status()
        data = resp.json().get("response", [])

        # Проверка: сколько матчей пришло
        await update.message.reply_text(f"📅 Найдено матчей: {len(data)}")

        # Если ничего нет — выходим
        if not data:
            await update.message.reply_text("⚠️ Нет матчей на сегодня.")
            return

        # Выводим первые 5 матчей
        messages = []
        for game in data[:5]:
            league = game["league"]["name"]
            home = game["teams"]["home"]["name"]
            away = game["teams"]["away"]["name"]
            status = game["fixture"]["status"]["short"]

            messages.append(f"🏆 {league}: {home} vs {away} ({status})")

        await update.message.reply_text("\n".join(messages))

    except Exception as e:
        import traceback
        await update.message.reply_text("❌ Ошибка:")
        await update.message.reply_text(traceback.format_exc())
