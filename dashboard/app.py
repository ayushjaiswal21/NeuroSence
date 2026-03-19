from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Global state to hold the latest reading
current_state = {
    "hr": 0,
    "rmssd": 0.0,
    "gsr": 0.0,
    "stress_alert": False,
    "timestamp": "No data yet"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/update', methods=['POST'])
def update_data():
    """Endpoint for MacroDroid or ESP32 to push new data."""
    global current_state
    data = request.json
    if data:
        current_state['hr'] = data.get('hr', current_state['hr'])
        current_state['rmssd'] = data.get('rmssd', current_state['rmssd'])
        current_state['gsr'] = data.get('gsr', current_state['gsr'])
        current_state['stress_alert'] = data.get('stress_alert', current_state['stress_alert'])
        
        import datetime
        current_state['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"status": "success", "message": "Data updated"})
    return jsonify({"status": "error", "message": "Invalid JSON"}), 400

@app.route('/api/data', methods=['GET'])
def get_data():
    """Endpoint for frontend to poll the latest data."""
    return jsonify(current_state)

if __name__ == '__main__':
    # Run the web application using dev server for prototyping
    app.run(host='0.0.0.0', port=5000, debug=True)
