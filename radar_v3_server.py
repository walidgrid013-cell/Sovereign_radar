from flask import Flask
import requests
import threading
import time
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except:
        pass

def radar_loop():
    send_telegram_message("✅ Sovereign Radar V3 Online\n24/7 شغال - الخطة المجانية")
    while True:
        # هنا من بعد تزيد الكود تاع الرادار تاعك
        time.sleep(300)

@app.route('/')
def home():
    return "Sovereign Radar V3 is running"

if __name__ == '__main__':
    threading.Thread(target=radar_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
