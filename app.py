from flask import Flask, request
import cv2
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

def analyze_leaf(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    average_color = image.mean(axis=0).mean(axis=0)
    green_percentage = (average_color[1] / 255) * 100
    return green_percentage

def predict_growing_days(temperature, humidity, soil_moisture):
    training_data = {
        '온도': [20, 25, 30, 35, 40],
        '습도': [30, 35, 40, 45, 50],
        '토양수분': [0.2, 0.4, 0.6, 0.8, 1.0],
        '재배_가능일': [60, 65, 70, 75, 80]
    }
    df = pd.DataFrame(training_data)
    X = df[['온도', '습도', '토양수분']]
    y = df['재배_가능일']
    model = LinearRegression()
    model.fit(X, y)
    new_data = {
        '온도': [temperature],
        '습도': [humidity],
        '토양수분': [soil_moisture]
    }
    df_new = pd.DataFrame(new_data)
    predicted_days = model.predict(df_new)
    return predicted_days[0]

@app.route('/upload_sensor_data', methods=['POST'])
def process_data():
    temperature = float(request.form.get('temp'))
    humidity = float(request.form.get('humi'))
    soil_moisture = float(request.form.get('soilMoisture'))
    predicted_days = predict_growing_days(temperature, humidity, soil_moisture)
    app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}".format(temperature, humidity, soil_moisture))
    response = {
        'predicted_days': predicted_days
    }
    return response
    
# @app.route('/upload_sensor_data', methods=['POST','GET']  )
# def upload_sensor_data():
#     temperature = float(request.form.get('temp'))
#     humidity = float(request.form.get('humi'))
#     soil_moisture = float(request.form.get('soilMoisture'))

#     # 데이터 처리 및 원하는 동작 수행
#     # 예시로 간단히 로그에 출력하고 응답을 생성하는 코드를 추가했습니다.
#     app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}".format(temperature, humidity, soil_moisture))
#     response = {
#         'message': 'Data received and processed successfully'
#     }
#     return response



@app.route('/upload_image', methods=['POST'])
def upload_image():
    image_file = request.files['image']
    if image_file:
        image_path = 'path/to/save/image.jpg'
        image_file.save(image_path)
    leaf_status = analyze_leaf(image_file)

    response = {
        'leaf_status': leaf_status,
    }
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
    