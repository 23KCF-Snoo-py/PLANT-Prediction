import json
import base64
import requests

def lambda_handler(event, context):
    image_path = 'path/to/image.png'  # 전송할 이미지 파일 경로
    endpoint_url = 'http://172.31.33.222:1234/upload_image'  # Flask 서버의 엔드포인트 URL

    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    data = {
        'image': image_data
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print('Image uploaded successfully')
    else:
        print('Failed to upload image')
