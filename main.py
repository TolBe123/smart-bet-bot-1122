import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import Conflict
import matplotlib.pyplot as plt
import io
import datetime

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ======== Команды ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["💰 Банк", "📊 График"], ["📌 Ставки", "✅ Сделано"], ["📈 Статистика"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Добро пожаловать! Выберите команду или нажмите кнопку:", reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start — запуск\n/recommendations — ставки\n/bank — банк\n/graph — график\n/stats — статистика\n/placed — сделанные ставки")

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока нет value-ставок. Скоро здесь будет ИИ-анализ.")

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Текущий банк: 1000₽")

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(5)][::-1]
    values = [1000, 1020, 980, 1050, 1100]

    plt.figure()
    plt.plot(dates, values, marker='o')
    plt.title("Баланс")
    plt.xlabel("Дата")
    plt.ylabel("₽")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await update.message.reply_photo(photo=buf)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Профит: +100₽\nСделано ставок: 5\nWinrate: 60%")

async def placed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сделанные ставки:\n1. 15.06 – Победа команды А – 2.1 (✅)\n2. 16.06 – ТБ(2.5) – 1.9 (❌)")

# ======== Основной код ========

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("recommendations", recommendations))
    app.add_handler(CommandHandler("bank", bank))
    app.add_handler(CommandHandler("graph", graph))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("placed", placed))

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

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    try:
        app.run_polling()
    except Conflict:
        logging.warning("⚠️ Bot is already running in another process.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
