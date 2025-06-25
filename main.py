import os
from telegram.ext import Application, CommandHandler
from live_command import live  # Только команда live
import threading

TOKEN = os.getenv("BOT_TOKEN") or "your_token_here"

app = Application.builder().token(TOKEN).build()

# Команды
app.add_handler(CommandHandler("live", live))

# Запуск бота
if __name__ == '__main__':
    print("Bot is running...")
    app.run_polling()
