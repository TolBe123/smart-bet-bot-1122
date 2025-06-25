import json
import asyncio
import websockets
import time

RAW_LOG_PATH = "raw.json"

async def fetch_live_value_bets(callback):
    url = "wss://ws-secure.1xbet.com/"
    log_count = 0
    max_logs = 5
    raw_messages = []

    async with websockets.connect(url) as ws:
        # Пример запроса (может быть изменён в зависимости от структуры)
        await ws.send(json.dumps({
            "command": "get",
            "params": {
                "sport": "1",  # Футбол
                "type": "live"
            }
        }))

        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)

                if log_count < max_logs:
                    raw_messages.append(data)
                    log_count += 1
                    if log_count == max_logs:
                        with open(RAW_LOG_PATH, "w", encoding="utf-8") as f:
                            json.dump(raw_messages, f, ensure_ascii=False, indent=2)
                        print(f"Saved first {max_logs} messages to {RAW_LOG_PATH}")

                # Пока не обрабатываем — ждём анализа структуры
                continue

            except Exception as e:
                print("Error in WebSocket loop:", e)
                await asyncio.sleep(5)

def extract_events(data):
    return []