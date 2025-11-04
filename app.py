from flask import Flask, render_template, request, jsonify
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  temperature REAL,
                  humidity REAL,
                  soil_moisture REAL,
                  ph REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS crops
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  temperature TEXT,
                  soil_moisture TEXT,
                  ph TEXT,
                  fertilizers TEXT,
                  pesticides TEXT,
                  soil_type TEXT,
                  additional_info TEXT)''')

    conn.commit()
    conn.close()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    # Simulate ESP32 data
    data = {
        'temperature': round(random.uniform(20, 35), 1),
        'humidity': round(random.uniform(50, 80), 1),
        'soil_moisture': round(random.uniform(30, 70), 1),
        'ph': round(random.uniform(5.5, 7.5), 1),
        'timestamp': datetime.now().isoformat()
    }

    # Saves to database
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute('''INSERT INTO sensor_data (timestamp, temperature, humidity, soil_moisture, ph)
                 VALUES (?, ?, ?, ?, ?)''',
              (data['timestamp'], data['temperature'], data['humidity'],
               data['soil_moisture'], data['ph']))
    conn.commit()
    conn.close()

    return jsonify(data)


# API endpoint for historical sensor data
@app.route('/api/sensor-history', methods=['GET'])
def get_sensor_history():
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 24''')
    rows = c.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'timestamp': row[1],
            'temperature': row[2],
            'humidity': row[3],
            'soil_moisture': row[4],
            'ph': row[5]
        })

    return jsonify(history)


# API endpoint for disease detection
@app.route('/api/analyze-disease', methods=['POST'])
def analyze_disease():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']

    # TODO: Integrate the ML model here
    result = {
        'disease': 'Late Blight',
        'confidence': '87%',
        'description': 'Fungal disease affecting leaves and stems. Common in humid conditions.',
        'treatment': 'Apply Mancozeb or Copper-based fungicides. Remove affected leaves immediately.',
        'prevention': 'Ensure proper spacing, avoid overhead watering, improve air circulation.'
    }

    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
