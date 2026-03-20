from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

EMAIL_SENDER = "your_project_email@gmail.com"
EMAIL_PASSWORD = "your_16_digit_app_password"
EMAIL_RECEIVER = "doctor_email@example.com"

def send_telegram_alert(bpm, rmssd):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = f"🚨 *EDGEMIND ALERT* 🚨\nHigh Cognitive Stress Detected!\n\n❤️ HR: {bpm} BPM\n📉 HRV: {rmssd} ms\n⏱ Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print("✅ Telegram Alert Sent!")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def send_email_alert(bpm, rmssd):
    subject = "URGENT: Patient Cognitive Stress Alert"
    body = f"Doctor, the EdgeMind wearable has detected a critical stress spike.\n\nMetrics:\n- Heart Rate: {bpm} BPM\n- HRV (RMSSD): {rmssd} ms\n\nPlease check the patient dashboard immediately."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email Alert Sent to Doctor!")
    except Exception as e:
        print(f"❌ Email Error: {e}")

# --- THE WEBHOOK ENDPOINT ---
@app.route('/webhook', methods=['POST'])
def receive_data():
    data = request.json
    bpm = data.get('bpm')
    rmssd = data.get('rmssd')
    stress = data.get('stress')
    
    print(f"📊 LIVE DATA RECEVIED -> HR: {bpm} | RMSSD: {rmssd} | Stress: {stress}")
    
    if stress == 1:
        print("\n⚠️ TRIGGERING EMERGENCY PROTOCOLS...")
        send_telegram_alert(bpm, rmssd)
        send_email_alert(bpm, rmssd)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Run server on all local IP addresses at port 5000
    print("🚀 EdgeMind Dashboard Server is Running...")
    app.run(host='0.0.0.0', port=5000)
