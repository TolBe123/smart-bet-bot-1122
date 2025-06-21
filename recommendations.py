
import os
import json
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

API_KEY = os.getenv("API_FOOTBALL_KEY")
BANK_FILE = "data/bank.json"
PLACED_FILE = "data/placed.json"

def get_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r") as f:
            return float(f.read())
    return 1000.0

def save_placed(bet):
    data = []
    if os.path.exists(PLACED_FILE):
        with open(PLACED_FILE, "r") as f:
            data = json.load(f)
    data.append(bet)
    with open(PLACED_FILE, "w") as f:
        json.dump(data, f)

def implied_prob(odd):
    return 1 / float(odd) if float(odd) > 0 else 0

def kelly(p, b):
    q = 1 - p
    return max((b * p - q) / b, 0)

def win_ratio(form: str):
    form = form.upper()
    if not form:
        return 0.33
    total = len(form)
    wins = form.count('W')
    return wins / total if total > 0 else 0.33

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    url = "https://api-football-v1.p.rapidapi.com/v3/odds?region=eu&bookmaker=1"

    try:
        response = requests.get(url, headers=headers)
        matches = response.json().get("response", [])[:5]

        messages = []

        for match in matches:
            league = match["league"]["name"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            teams = f"{home} vs {away}"

            try:
                form_home = match["teams"]["home"]["form"]
                form_away = match["teams"]["away"]["form"]
            except:
                continue

            win_home = win_ratio(form_home)
            win_away = win_ratio(form_away)
            draw_chance = 1.0 - win_home - win_away
            draw_chance = max(0.15, min(draw_chance, 0.35))  # ограничим вменяемыми рамками

            bets = match["bookmakers"][0]["bets"][0]["values"]

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
                        f"🏆 {league}
"
                        f"⚽ {teams}
"
                        f"📌 Bet: {outcome_name}
"
                        f"📊 Odds: {odd:.2f} → Implied: {implied*100:.1f}%
"
                        f"📈 Model probability: {p*100:.1f}% (based on form: {form_home} / {form_away})
"
                        f"✅ Value: {value_score*100:.2f}%
"
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
            await update.message.reply_text("No value bets found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
