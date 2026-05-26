from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
import os

TOKEN = "8630546908:AAGJFPluYgvyqhVO-43DMDizGrYknDvJbjc"

expenses = []

web_app = Flask("")

@web_app.route("/")
def home():
    return "Budget bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send an expense like this:\n\nCamilla coffee 4500\nJames restaurant 32000\nShared supermarket 78000"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        parts = text.split()

        person = parts[0]
        category = parts[1]
        amount = int(parts[2])

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
            "Error 😢\nSend it like this:\nCamilla coffee 4500"
        )

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_amount = sum(item["amount"] for item in expenses)

    await update.message.reply_text(
        f"Total expenses: {total_amount} won"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("total", total))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

Thread(target=run_web, daemon=True).start()

print("BOT STARTED")

app.run_polling(drop_pending_updates=True)
