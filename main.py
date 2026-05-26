from flask import Flask, request
import requests
import os
import json
import gspread

from google.oauth2.service_account import Credentials
from datetime import datetime

TOKEN = os.environ["BOT_TOKEN"]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open("BudgetBot Expenses").sheet1

app = Flask(__name__)

user_state = {}

CATEGORIES = [
    ["☕ Coffee", "🍽 Restaurant"],
    ["🛒 Supermarket", "🥡 Delivery"],
    ["🚕 Taxi", "👗 Clothes"],
    ["💄 Beauty", "💊 Health"],
    ["🏠 Home", "🎁 Gifts"],
    ["✈️ Travel", "🎬 Entertainment"],
]

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    requests.post(url, json=payload)

@app.route("/")
def home():
    return "Budget bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "Choose a category:",
            CATEGORIES
        )

    elif text == "/total":
        records = sheet.get_all_records()

        total = sum(int(row["Amount"]) for row in records)

        send_message(
            chat_id,
            f"Total expenses: {total} KRW"
        )

    elif text in [item for row in CATEGORIES for item in row]:

        category = text.split(" ", 1)[1]

        user_state[chat_id] = {
            "category": category
        }

        send_message(
            chat_id,
            f"How much did you spend on {category}?"
        )

    else:
        try:
            amount = int(text)

            category = user_state[chat_id]["category"]

            sheet.append_row([
                str(datetime.now()),
                "Camilla",
                category,
                amount,
                "KRW"
            ])

            send_message(
                chat_id,
                f"Added: {category} — {amount} KRW",
                CATEGORIES
            )

        except:
            send_message(
                chat_id,
                "Please choose category first.",
                CATEGORIES
            )

    return "ok"

@app.route("/set_webhook")
def set_webhook():

    webhook_url = "https://budgetboy.onrender.com/webhook"

    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"

    response = requests.get(url)

    return response.text
