
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import csv
import os
import matplotlib.pyplot as plt
from datetime import date

BOT_TOKEN = "8119762447:AAHhuYfXHhSXSXGYXbqhCLwQdyqtBIUzmjo"
AUTHORIZED_USER_ID = 1325161910
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "history.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"start_bank": 1000, "current_bank": 1000}, f)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def append_history(row):
    write_header = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Date", "Match", "Pick", "Odds", "Bet", "Result", "Profit", "Bank"])
        writer.writerow(row)

def plot_bank_history():
    if not os.path.exists(HISTORY_FILE):
        return None
    dates, banks = [], []
    with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(row["Date"])
            banks.append(float(row["Bank"]))
    if not banks:
        return None
    plt.figure(figsize=(10, 5))
    plt.plot(dates, banks, marker='o')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.title("📈 График изменения банка")
    plt.xlabel("Дата")
    plt.ylabel("Банк (₽)")
    plt.tight_layout()
    image_path = "bank_chart.png"
    plt.savefig(image_path)
    plt.close()
    return image_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🎯 Добро пожаловать в ИИ-помощник ставок. Команды: /банк, /график, /поставил")

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    s = load_settings()
    await update.message.reply_text(f"💰 Текущий банк: {s['current_bank']}₽")

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    chart_path = plot_bank_history()
    if chart_path:
        await update.message.reply_photo(photo=InputFile(chart_path))
    else:
        await update.message.reply_text("❌ Недостаточно данных для графика.")

async def placed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    try:
        text = update.message.text.replace("/поставил", "").strip()
        parts = text.split(",")
        if len(parts) != 5:
            await update.message.reply_text("⚠ Формат: /поставил Арсенал - Ливерпуль, Home, 2.10, 100, Win/Loss")
            return
        match, pick, odds, bet, result = [p.strip() for p in parts]
        odds = float(odds)
        bet = float(bet)
        profit = round((odds - 1) * bet, 2) if result.lower() == "win" else -bet
        s = load_settings()
        s["current_bank"] += profit
        save_settings(s)
        append_history([str(date.today()), match, pick, odds, bet, result, profit, s["current_bank"]])
        await update.message.reply_text(f"✅ Записано. Профит: {profit}₽. Новый банк: {s['current_bank']}₽")
    except Exception as e:
        logger.error(str(e))
        await update.message.reply_text("❌ Ошибка при обработке. Проверь формат.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("банк", bank))
    app.add_handler(CommandHandler("график", graph))
    app.add_handler(CommandHandler("поставил", placed))
    app.run_polling()

if __name__ == "__main__":
    main()
