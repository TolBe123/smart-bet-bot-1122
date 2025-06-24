import os
from telegram.ext import Application, CommandHandler
from recommendations import recommendations
from live_command import live
from flashscore_ws import start_ws
import threading

TOKEN = os.getenv("BOT_TOKEN") or "your_token_here"

app = Application.builder().token(TOKEN).build()

# Команды
app.add_handler(CommandHandler("recommendations", recommendations))
app.add_handler(CommandHandler("live", live))

# Запуск Flashscore WebSocket в фоне
t = threading.Thread(target=start_ws, daemon=True)
t.start()

# Запуск бота
if __name__ == '__main__':
    print("Bot is running...")
    app.run_polling()
