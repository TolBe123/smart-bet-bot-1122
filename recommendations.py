async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "x-apisports-key": API_KEY
    }

    # Получаем матчи на сегодня
    today = datetime.today().strftime('%Y-%m-%d')
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?date={today}"

    try:
        resp = requests.get(fixtures_url, headers=headers)
        data = resp.json().get("response", [])

        if not data:
            await update.message.reply_text("⚠️ No matches found for today.")
            return

        messages = []

        for game in data[:10]:  # Ограничим до 10 матчей
            fixture_id = game["fixture"]["id"]
            league = game["league"]["name"]
            home = game["teams"]["home"]["name"]
            away = game["teams"]["away"]["name"]
            teams = f"{home} vs {away}"

            # Получаем коэффициенты
            odds_url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}&bookmaker=1"
            odds_resp = requests.get(odds_url, headers=headers)
            odds_data = odds_resp.json().get("response", [])

            if not odds_data:
                continue

            try:
                bets = odds_data[0]["bookmakers"][0]["bets"][0]["values"]
            except (IndexError, KeyError):
                continue

            form_home = game["teams"]["home"].get("form", "")
            form_away = game["teams"]["away"].get("form", "")

            win_home = win_ratio(form_home)
            win_away = win_ratio(form_away)
            draw_chance = 1.0 - win_home - win_away
            draw_chance = max(0.15, min(draw_chance, 0.35))

            for outcome in bets:
                outcome_name = outcome["value"]
                odd = float(outcome["odd"])
                b = odd - 1

                if outcome_name == "Home":
                    p = win_home
                elif outcome_name == "Away":
                    p = win_away
                elif outcome_name == "Draw":
                    p = draw_chance
                else:
                    continue

                value_score = (p * odd) - 1
                kelly_frac = kelly(p, b)

                if value_score > 0 and kelly_frac > 0:
                    stake = round(get_bank() * kelly_frac, 2)
                    implied = implied_prob(odd)

                    text = (
                        f"🏆 {league}\n"
                        f"⚽ {teams}\n"
                        f"📌 Bet: {outcome_name}\n"
                        f"📊 Odds: {odd:.2f} → Implied: {implied*100:.1f}%\n"
                        f"📈 Model probability: {p*100:.1f}% (based on form)\n"
                        f"✅ Value: {value_score*100:.2f}%\n"
                        f"🎯 Kelly stake: {kelly_frac*100:.2f}% → {stake}₽"
                    )

                    messages.append(text)

                    save_placed({
                        "match": teams,
                        "bet": outcome_name,
                        "odd": odd,
                        "stake": stake,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })

                    break

        if messages:
            await update.message.reply_text("\n\n".join(messages))
        else:
            await update.message.reply_text("🟡 No value bets found today.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
