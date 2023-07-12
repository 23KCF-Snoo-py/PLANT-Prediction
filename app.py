from flask import Flask, request
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

def predict_growing_days(temperature, humidity, soil_moisture):
    training_data = {
        '온도': [20, 25, 30, 35, 40],
        '습도': [30, 35, 40, 45, 50],
        '토양수분': [0.2, 0.4, 0.6, 0.8, 1.0],
        '상추': [60, 65, 70, 75, 80],
        '허브': [50, 55, 60, 65, 70],
        '딸기': [70, 75, 80, 85, 90],
        '토마토': [80, 85, 90, 95, 100],
        '바질': [55, 60, 65, 70, 75],
        '샐러리': [65, 70, 75, 80, 85],
        '케일': [45, 50, 55, 60, 65]
    }
    df = pd.DataFrame(training_data)
    X = df[['온도', '습도', '토양수분']]
    y = df[['상추', '허브', '딸기', '토마토', '바질', '샐러리', '케일']]
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

@app.route('/predict_all', methods=['POST'])
def predict_all_plants():
    temperature = float(request.form.get('temperature'))
    humidity = float(request.form.get('humidity'))
    soil_moisture = float(request.form.get('soil_moisture'))
    predicted_days = predict_growing_days(temperature, humidity, soil_moisture)
    app.logger.debug("Received data - Temperature: {}, Humidity: {}, Soil Moisture: {}".format(temperature, humidity, soil_moisture))
    
    plant_names = ['상추', '허브', '딸기', '토마토', '바질', '샐러리', '케일']
    predicted_days_dict = dict(zip(plant_names, predicted_days))
    
    response = {
        'predicted_days': predicted_days_dict
    }
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
