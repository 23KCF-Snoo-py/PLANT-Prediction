from PIL import Image
import io
from flask import Flask, request, jsonify
import cv2
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import logging
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

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
    if request.method == 'POST':
        temperature = float(request.form.get('Temp'))
        humidity = float(request.form.get('humi'))
        soil_moisture = float(request.form.get('soil'))
        predicted_days = predict_growing_days(temperature, humidity, soil_moisture)

        app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}".format(temperature, humidity, soil_moisture))
        app.logger.debug(predicted_days)

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

            # Check if the predicted_leaf_status is available
            if 'predicted_leaf_status' in globals():
                # Return the predicted_leaf_status as JSON response for the GET request
                response = {
                    'leaf_status': predicted_leaf_status,
                }
                return jsonify(response)
            else:
                return jsonify({"status": "error", "message": "예측된 데이터가 없습니다."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

@app.route('/upload_image', methods=['POST', 'GET'])
def upload_image():
    global predicted_leaf_status
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename != '':
                    # Save the received image temporarily
                    image_data = image_file.read()
                    image = Image.open(io.BytesIO(image_data))

                    # Convert the image to JPEG format and get the binary data
                    jpg_image = io.BytesIO()
                    image.save(jpg_image, format='JPEG')
                    jpg_image.seek(0)
                    jpg_data = jpg_image.getvalue()

                    # Process the image (e.g., analyze it)
                    leaf_status = analyze_leaf(cv2.imdecode(np.frombuffer(jpg_data, np.uint8), cv2.COLOR_BGR2RGB))

                    # Log the leaf_status along with other information
                    app.logger.debug("Received image and analyzed leaf_status: {}".format(leaf_status))

                    # Store the leaf_status value in the global variable to use later for GET request
                    predicted_leaf_status = leaf_status

                    # Return the analysis result as JSON response
                    response = {
                        'leaf_status': leaf_status,
                    }
                    return jsonify(response)

            return jsonify({"status": "error", "message": "No image found in the request"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    elif request.method == 'GET':
        try:
            app.logger.debug("GET request received.")
            app.logger.debug("Predicted leaf_status for GET request: {}".format(predicted_leaf_status))

            # Check if the predicted_leaf_status is available
            if predicted_leaf_status is not None:
                # Return the predicted_leaf_status as JSON response for the GET request
                response = {
                    'leaf_status': predicted_leaf_status,
                }
                return jsonify(response)
            else:
                return jsonify({"status": "error", "message": "No predicted data available."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
