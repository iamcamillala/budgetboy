from flask import Flask, request
import requests

TOKEN = "8630546908:AAGJFPluYgvyqhVO-43DMDizGrYknDvJbjc"

app = Flask(__name__)
expenses = []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/")
def home():
    return "Budget bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Hi! Send expense like:\nCamilla coffee 4500")
        elif text == "/total":
            total = sum(item["amount"] for item in expenses)
            send_message(chat_id, f"Total expenses: {total} won")
        else:
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

                send_message(chat_id, f"Added: {person} | {category} | {amount} won")
            except:
                send_message(chat_id, "Error 😢\nExample:\nCamilla coffee 4500")

    return "ok"

@app.route("/set_webhook")
def set_webhook():
    webhook_url = "https://budgetboy.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return response.text
