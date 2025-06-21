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
        "x-apisports-key": API_KEY
    }

    # Пример: Англия - Премьер-лига (league=39), сезон 2024
    url = "https://v3.football.api-sports.io/odds?league=39&season=2024&bookmaker=1"

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
                form_home = match["teams"]["home"].get("form", "")
                form_away = match["teams"]["away"].get("form", "")
            except:
                continue

            win_home = win_ratio(form_home)
            win_away = win_ratio(form_away)
            draw_chance = 1.0 - win_home - win_away
            draw_chance = max(0.15, min(draw_chance, 0.35))

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
                    stake = round(get_bank() * kelly_frac,
