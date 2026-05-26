from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8630546908:AAGJFPluYgvyqhVO-43DMDizGrYknDvJbjc"

expenses = []

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Budget bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send expense like:\nCamilla coffee 4500"
    )

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_sum = sum(item["amount"] for item in expenses)

    await update.message.reply_text(
        f"Total expenses: {total_sum} won"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.split()

        person = text[0]
        category = text[1]
        amount = int(text[2])

        expenses.append({
            "person": person,
            "category": category,
            "amount": amount
        })

        await update.message.reply_text(
            f"Added: {person} | {category} | {amount} won"
        )

    except:
        await update.message.reply_text(
            "Error 😢\nExample:\nCamilla coffee 4500"
        )

telegram_app = ApplicationBuilder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("total", total))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

Thread(target=run_web).start()

print("BOT STARTED")

telegram_app.run_polling()
