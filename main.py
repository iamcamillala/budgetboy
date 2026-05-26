from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

expenses = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь расход так:\n\nКамилла кофе 4500"
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
            f"Добавлено: {person} | {category} | {amount} вон"
        )

    except:
        await update.message.reply_text(
            "Ошибка 😢\nПиши так:\nКамилла кофе 4500"
        )

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_amount = sum(item["amount"] for item in expenses)

    await update.message.reply_text(
        f"Общие расходы: {total_amount} вон"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("total", total))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
