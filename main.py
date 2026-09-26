import asyncio
import websockets
import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

DERIV_TOKEN = os.environ.get("DERIV_TOKEN")
APP_ID = "1089"

async def trade(action, symbol="frxXAUUSD", amount=1):
    url = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
        await ws.recv()
        contract_type = "CALL" if action == "BUY" else "PUT"
        await ws.send(json.dumps({
            "buy": 1,
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 5,
                "duration_unit": "m",
                "symbol": symbol
            }
        }))
        result = json.loads(await ws.recv())
        return result

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")
    symbol = data.get("symbol", "frxXAUUSD")
    amount = float(data.get("amount", 1))
    if action in ["BUY", "SELL"]:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(trade(action, symbol, amount))
        return jsonify({"status": "done", "result": str(result)})
    return jsonify({"status": "no action"})

@app.route('/')
def home():
    return "Bot is Running! ✅"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
