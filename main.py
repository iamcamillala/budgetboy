from flask import Flask, request
import requests

TOKEN = "8630546908:AAGJFPluYgvyqhVO-43DMDizGrYknDvJbjc"

app = Flask(__name__)
expenses = []
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
    payload = {"chat_id": chat_id, "text": text}

    if keyboard:
        payload["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False
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
            "Hi! Choose a category:",
            CATEGORIES
        )

    elif text == "/total":
        total = sum(item["amount"] for item in expenses)
        send_message(chat_id, f"Total expenses: {total} won")

    elif text in [item for row in CATEGORIES for item in row]:
        category = text.split(" ", 1)[1]
        user_state[chat_id] = {"category": category}
        send_message(chat_id, f"How much did you spend on {category}?")

    else:
        try:
            amount = int(text)
            category = user_state[chat_id]["category"]

            expenses.append({
                "category": category,
                "amount": amount
            })

            send_message(
                chat_id,
                f"Added: {category} — {amount} won",
                CATEGORIES
            )

        except:
            send_message(
                chat_id,
                "Please choose a category first, then enter the amount.",
                CATEGORIES
            )

    return "ok"

@app.route("/set_webhook")
def set_webhook():
    webhook_url = "https://budgetboy.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return response.text
