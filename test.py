import requests

# Flask 서버 주소와 엔드포인트 지정
server_url = "http://172.31.33.222:1234/upload_sensor_data"

# GET 요청에 사용할 데이터 지정
data = {
    'Temp': 25.0,
    'humi': 40.0,
    'soil': 0.6,
    'cds': 300.0
}

# GET 요청 보내기
response = requests.get(server_url, params=data)

# 응답 처리
if response.status_code == 200:
    result = response.json()
    print("Predicted Days:")
    for plant, days in result['predicted_days'].items():
        print(f"{plant}: {days}")
else:
    print("Failed to get predicted days. Status code:", response.status_code)
