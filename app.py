from PIL import Image
import io
from flask import Flask, request, jsonify
import cv2
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

def analyze_leaf(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    average_color = image.mean(axis=0).mean(axis=0)
    green_percentage = (average_color[1] / 255) * 100
    return green_percentage

def predict_growing_days(temperature, humidity, soil_moisture, cds):
    training_data = {
        'temp': [20, 25, 30, 35, 40],
        'humi': [30, 35, 40, 45, 50],
        'soilMoisture': [0.2, 0.4, 0.6, 0.8, 1.0],
        'cds': [100, 200, 300, 400, 500],  # 가정한 조도(빛의 밝기) 값
        'Lettuce': [60, 65, 70, 75, 80],
        'Basil': [50, 55, 60, 65, 70],
        'Strawberry': [70, 75, 80, 85, 90],
        'Tomato': [80, 85, 90, 95, 100],
        'Herb': [55, 60, 65, 70, 75],
        'Celery': [65, 70, 75, 80, 85],
        'Kale': [45, 50, 55, 60, 65]
    }
    df = pd.DataFrame(training_data)
    X = df[['temp', 'humi', 'soilMoisture', 'cds']]
    y = df[['Lettuce', 'Basil', 'Strawberry', 'Tomato', 'Herb', 'Celery', 'Kale']]
    model = LinearRegression()
    model.fit(X, y)
    new_data = {
        'temp': [temperature],
        'humi': [humidity],
        'soilMoisture': [soil_moisture],
        'cds': [cds]
    }
    df_new = pd.DataFrame(new_data)
    predicted_days = model.predict(df_new)
    return predicted_days[0]

@app.route('/upload_sensor_data', methods=['POST', 'GET'])
def process_data():
    if request.method == 'POST':
        temperature = float(request.form.get('Temp'))
        humidity = float(request.form.get('humi'))
        soil_moisture = float(request.form.get('soil'))
        cds = float(request.form.get('cds'))
    elif request.method == 'GET':
        temperature = float(request.args.get('Temp'))
        humidity = float(request.args.get('humi'))
        soil_moisture = float(request.args.get('soil'))
        cds = float(request.args.get('cds'))
    else:
        return jsonify({'error': 'Method not allowed'}), 405

    predicted_days = predict_growing_days(temperature, humidity, soil_moisture, cds)
    app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}, CDS: {}".format(temperature, humidity, soil_moisture, cds))
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
    
@app.route('/upload_image', methods=['POST'])
def upload_image():
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
                app.logger.info("Leaf Status: {}".format(leaf_status))
                # Return the analysis result
                response = {
                    'leaf_status': leaf_status,
                }
                return jsonify(response)

        return jsonify({"status": "error", "message": "No image found in the request"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
