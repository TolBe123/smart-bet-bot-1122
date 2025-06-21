
import os
import logging
from telegram.ext import Application, CommandHandler
from telegram.error import Conflict
from commands import start, help_command, recommendations, bank, graph, stats, placed
from telegram import ReplyKeyboardMarkup

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()

    # Кнопочная клавиатура
    keyboard = ReplyKeyboardMarkup(
        [["💰 Банк", "📊 График"], ["📌 Ставки", "✅ Сделано"], ["📈 Статистика"]],
        resize_keyboard=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("recommendations", recommendations))
    app.add_handler(CommandHandler("bank", bank))
    app.add_handler(CommandHandler("graph", graph))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("placed", placed))

    # Текстовые кнопки
    async def handle_buttons(update, context):
        text = update.message.text.strip()
        if text == "💰 Банк":
            await bank(update, context)
        elif text == "📊 График":
            await graph(update, context)
        elif text == "📌 Ставки":
            await recommendations(update, context)
        elif text == "✅ Сделано":
            await placed(update, context)
        elif text == "📈 Статистика":
            await stats(update, context)

    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    try:
        app.run_polling()
    except Conflict:
        logging.warning("⚠️ Bot is already running in another process. Skipping second instance.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
