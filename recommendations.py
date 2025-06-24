async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "x-apisports-key": API_KEY
    }

    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"

    try:
        resp = requests.get(url, headers=headers)
        data = resp.json().get("response", [])
        await update.message.reply_text(f"📅 Найдено матчей: {len(data)}")

        if data:
            preview = [f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}" for match in data[:5]]
            await update.message.reply_text("🔍 Примеры:\n" + "\n".join(preview))
        else:
            await update.message.reply_text("⚠️ Нет матчей на сегодня.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
