import os
from telegram.ext import Application, CommandHandler
from recommendations import recommendations
from live_command import live
from flashscore_ws import start_ws
import threading

# Получаем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "your_token_here"

# Создание Telegram приложения
app = Application.builder().token(TOKEN).build()

# Подключаем команды
app.add_handler(CommandHandler("recommendations", recommendations))
app.add_handler(CommandHandler("live", live))

# Запуск Flashscore WebSocket в отдельном потоке
t = threading.Thread(target=start_ws, daemon=True)
t.start()

# Запуск Telegram-бота
if __name__ == '__main__':
    print("Bot is running...")
    app.run_polling()
if __name__ == '__main__':
    application.run_polling(drop_pending_updates=True)
