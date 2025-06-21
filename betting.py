import requests
import os

API_KEY = os.getenv("API_FOOTBALL_KEY")
API_URL = "https://v3.football.api-sports.io/fixtures"

def get_value_bets():
    headers = {
        "x-apisports-key": API_KEY
    }
    params = {
        "date": "2025-06-21",
        "timezone": "Europe/Moscow"
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        data = response.json()
        bets = []

        for match in data.get("response", []):
            teams = match["teams"]
            league = match["league"]
            odds_data = match.get("odds")

            if not odds_data:
                continue

            odds = odds_data.get("1x2", {})
            if not odds or "1" not in odds or "2" not in odds:
                continue

            home_odds = float(odds["1"])
            away_odds = float(odds["2"])

            if home_odds <= 1 or away_odds <= 1:
                continue

            # Вычисление implied probability и value
            home_prob = 1 / home_odds
            fair_odds = 1 / home_prob
            value = round((home_odds - fair_odds) / fair_odds * 100, 2)

            if value >= 5:
                bets.append({
                    "match": f"{teams['home']['name']} vs {teams['away']['name']}",
                    "bet": "Победа хозяев",
                    "odds": home_odds,
                    "value": value,
                    "kelly": round((home_odds * home_prob - (1 - home_prob)) / home_odds * 100, 2)
                })

        return bets

    except Exception as e:
        return []

