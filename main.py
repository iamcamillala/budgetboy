from flask import Flask, request
import requests
import os
import json
import gspread

from google.oauth2.service_account import Credentials
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

user_state = {}

MAIN_MENU = [
    ["➕ Add expense"],
    ["📊 Statistics"],
]

CATEGORIES = [
    ["☕ Coffee", "🍽 Restaurant"],
    ["🛒 Supermarket", "🥡 Delivery"],
    ["🚕 Taxi", "👗 Clothes"],
    ["💄 Beauty", "💊 Health"],
    ["🏠 Home", "🎁 Gifts"],
    ["✈️ Travel", "🎬 Entertainment"],
    ["⬅️ Back"]
]

PERIODS = [
    ["📅 This month"],
    ["🗓 This year"],
    ["🌍 All time"],
    ["⬅️ Back"]
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

    response = requests.post(url, json=payload)

    return response

def get_sheet():

    creds_json = os.environ.get("GOOGLE_CREDENTIALS")

    creds_dict = json.loads(creds_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )

    client = gspread.authorize(creds)

    return client.open("BudgetBot").sheet1

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
            "Main menu:",
            MAIN_MENU
        )

    elif text == "➕ Add expense":

        send_message(
            chat_id,
            "Choose category:",
            CATEGORIES
        )

    elif text == "📊 Statistics":

        send_message(
            chat_id,
            "Choose period:",
            PERIODS
        )

    elif text == "⬅️ Back":

        send_message(
            chat_id,
            "Main menu:",
            MAIN_MENU
        )

    elif text in [item for row in CATEGORIES for item in row]:

        category = text.split(" ", 1)[1]

        user_state[chat_id] = {
            "mode": "expense",
            "category": category
        }

        send_message(
            chat_id,
            f"How much did you spend on {category}?"
        )

    elif text in ["📅 This month", "🗓 This year", "🌍 All time"]:

        try:

            sheet = get_sheet()

            records = sheet.get_all_records()

            total = 0

            for row in records:

                amount = row.get("Amount")

                if amount:
                    total += int(amount)

            send_message(
                chat_id,
                f"Total expenses:\n\n{total:,} KRW",
                MAIN_MENU
            )

        except Exception as e:

            error_text = f"{type(e).__name__}: {str(e)}"

            if hasattr(e, "response"):
                error_text += f"\n\nResponse text:\n{e.response.text}"

            send_message(
                chat_id,
                f"Statistics error:\n{error_text}",
                MAIN_MENU
            )

    else:

        try:

            amount = int(text)

            category = user_state[chat_id]["category"]

            sheet = get_sheet()

            sheet.append_row([
                str(datetime.now()),
                "Camilla",
                category,
                amount,
                "KRW"
            ])

            send_message(
                chat_id,
                f"Added:\n{category} — {amount:,} KRW",
                MAIN_MENU
            )

        except Exception as e:

            error_text = f"{type(e).__name__}: {str(e)}"

            if hasattr(e, "response"):
                error_text += f"\n\nResponse text:\n{e.response.text}"

            send_message(
                chat_id,
                f"Error:\n{error_text}",
                MAIN_MENU
            )

    return "ok"

@app.route("/set_webhook")
def set_webhook():

    webhook_url = "https://budgetboy.onrender.com/webhook"

    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"

    response = requests.get(url)

    return response.text
