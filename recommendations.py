import json
import asyncio
import websockets

RAW_LOG_PATH = "/tmp/raw.json"  # безопасный путь на Render

async def fetch_live_value_bets(callback):
    url = "wss://ws-secure.1xbet.com/"
    log_count = 0
    max_logs = 5
    raw_messages = []

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "command": "get",
            "params": {
                "sport": "1",
                "type": "live"
            }
        }))

        while True:
            try:
                response = await ws.recv()
                print("📥 Got response from 1xBet WebSocket", flush=True)
                data = json.loads(response)

                if log_count < max_logs:
                    raw_messages.append(data)
                    log_count += 1
                    if log_count == max_logs:
                        with open(RAW_LOG_PATH, "w", encoding="utf-8") as f:
                            json.dump(raw_messages, f, ensure_ascii=False, indent=2)
                        print(f"✅ Saved raw.json to {RAW_LOG_PATH}", flush=True)

                continue

            except Exception as e:
                print("❌ Error in WebSocket loop:", e, flush=True)
                await asyncio.sleep(5)

def extract_events(data):
    return []
