import websocket
import threading
import json
from datetime import datetime

WS_URL = "wss://push-performgroup.com/v3/zones/football"

live_matches = {}

def format_match(data):
    try:
        home = data.get("homeTeam", {}).get("name", "?")
        away = data.get("awayTeam", {}).get("name", "?")
        score = data.get("score", "?")
        minute = data.get("minute", "?")
        return f"{minute}' {home} {score} {away}"
    except:
        return "[Invalid Match Format]"

def on_message(ws, message):
    try:
        data = json.loads(message)
        for event in data.get("events", []):
            event_type = event.get("type")
            if event_type == "update":
                match_id = event.get("id")
                payload = event.get("data", {})
                live_matches[match_id] = payload
                readable = format_match(payload)
                print(f"[LIVE] {match_id}: {readable}")

                if "score" in payload and ":" in payload["score"]:
                    home_goals, away_goals = map(int, payload["score"].split(":"))
                    if home_goals + away_goals >= 1:
                        print(f"\n⚽ {readable} → LIKELY VALUE GAME\n")

    except Exception as e:
        print(f"[ERROR] Failed to parse message: {e}")

def on_error(ws, error):
    print(f"[ERROR] WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[INFO] WebSocket closed: {close_status_code} {close_msg}")

def on_open(ws):
    print("[INFO] WebSocket connection opened")

def start_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
