from PIL import Image
import io
from flask import Flask, request, jsonify, g
import cv2
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import logging
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

# Function to get the database connection for the current thread
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('predicted_data.db')
    return g.db

# Create a table for predicted data if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS predicted_data (
                id INTEGER PRIMARY KEY,
                lettuce REAL,
                basil REAL,
                strawberry REAL,
                tomato REAL,
                herb REAL,
                celery REAL,
                kale REAL
            )
        ''')
        db.commit()

# Function to store predicted data in the database
def store_predicted_data(predicted_days):
    db = get_db()
    c = db.cursor()
    c.execute('INSERT INTO predicted_data (lettuce, basil, strawberry, tomato, herb, celery, kale) VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(predicted_days))
    db.commit()

def analyze_leaf(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    average_color = image.mean(axis=0).mean(axis=0)
    green_percentage = (average_color[1] / 255) * 100
    return green_percentage
    
def predict_growing_days(temperature, humidity, soil_moisture):
    training_data = {
        'temp': [20, 25, 30, 35, 40],
        'humi': [30, 35, 40, 45, 50],
        'soilMoisture': [0.2, 0.4, 0.6, 0.8, 1.0],
        'Lettuce': [60, 65, 70, 75, 80],
        'Basil': [50, 55, 60, 65, 70],
        'Strawberry': [70, 75, 80, 85, 90],
        'Tomato': [80, 85, 90, 95, 100],
        'Herb': [55, 60, 65, 70, 75],
        'Celery': [65, 70, 75, 80, 85],
        'Kale': [45, 50, 55, 60, 65]
    }
    df = pd.DataFrame(training_data)
    X = df[['temp', 'humi', 'soilMoisture']]
    y = df[['Lettuce', 'Basil', 'Strawberry', 'Tomato', 'Herb', 'Celery', 'Kale']]
    model = LinearRegression()
    model.fit(X, y)
    new_data = {
        'temp': [temperature],
        'humi': [humidity],
        'soilMoisture': [soil_moisture]
    }
    df_new = pd.DataFrame(new_data)
    predicted_days = model.predict(df_new)
    return predicted_days[0]

@app.route('/upload_sensor_data', methods=['POST', 'GET'])
def process_data():
    global predicted_leaf_status
    global last_uploaded_data
    if request.method == 'POST':
        temperature = float(request.form.get('Temp'))
        humidity = float(request.form.get('humi'))
        soil_moisture = float(request.form.get('soil'))
        predicted_days = predict_growing_days(temperature, humidity, soil_moisture)

        app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}".format(temperature, humidity, soil_moisture))
        app.logger.debug(predicted_days)

        # Store the predicted data in the database
        store_predicted_data(predicted_days)

        last_uploaded_data['temperature'] = temperature
        last_uploaded_data['humidity'] = humidity
        last_uploaded_data['soil_moisture'] = soil_moisture

        response = {
            'predicted_days': {
                'Lettuce': predicted_days[0],
                'Basil': predicted_days[1],
                'Strawberry': predicted_days[2],
                'Tomato': predicted_days[3],
                'Herb': predicted_days[4],
                'Celery': predicted_days[5],
                'Kale': predicted_days[6]
            }
        }
        return jsonify(response)

    elif request.method == 'GET':
        try:
            app.logger.debug("GET request received.")
            
            # Retrieve the latest predicted data from the database
            db = get_db()
            c = db.cursor()
            c.execute('SELECT lettuce, basil, strawberry, tomato, herb, celery, kale FROM predicted_data ORDER BY id DESC LIMIT 1')
            row = c.fetchone()
            if row is not None:
                predicted_days = row
                # Return the predicted data as JSON response for the GET request
                response = {
                    'predicted_days': {
                        'Lettuce': predicted_days[0],
                        'Basil': predicted_days[1],
                        'Strawberry': predicted_days[2],
                        'Tomato': predicted_days[3],
                        'Herb': predicted_days[4],
                        'Celery': predicted_days[5],
                        'Kale': predicted_days[6]
                    }
                },
            elif last_uploaded_data['temperature'] is not None:
                response = {
                    'temperature': last_uploaded_data['temperature'],
                    'humidity': last_uploaded_data['humidity'],
                    'soil_moisture': last_uploaded_data['soil_moisture']
                }
                return jsonify(response)
            else:
                return jsonify({"status": "error", "message": "No predicted data available."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

# ... (existing code for uploading and analyzing image)

if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(host='0.0.0.0', port=1234, debug=True)