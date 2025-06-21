
import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import Conflict
from telegram import ReplyKeyboardMarkup
import start, help_command, recommendations, bank, graph, stats, placed

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()

    keyboard = ReplyKeyboardMarkup(
        [["💰 Банк", "📊 График"], ["📌 Ставки", "✅ Сделано"], ["📈 Статистика"]],
        resize_keyboard=True
    )

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CommandHandler("help", help_command.help_command))
    app.add_handler(CommandHandler("recommendations", recommendations.recommendations))
    app.add_handler(CommandHandler("bank", bank.bank))
    app.add_handler(CommandHandler("graph", graph.graph))
    app.add_handler(CommandHandler("stats", stats.stats))
    app.add_handler(CommandHandler("placed", placed.placed))

    async def handle_buttons(update, context):
        text = update.message.text.strip()
        if text == "💰 Банк":
            await bank.bank(update, context)
        elif text == "📊 График":
            await graph.graph(update, context)
        elif text == "📌 Ставки":
            await recommendations.recommendations(update, context)
        elif text == "✅ Сделано":
            await placed.placed(update, context)
        elif text == "📈 Статистика":
            await stats.stats(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    async def run_bot():
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logging.info("✅ Bot started successfully with polling.")
            await asyncio.Event().wait()
        except Conflict:
            logging.warning("⚠️ Conflict: Bot is already running elsewhere. Only one instance can poll updates.")
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}")

    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
