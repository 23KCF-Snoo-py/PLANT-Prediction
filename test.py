import requests

# GET 요청을 보낼 서버의 주소
url = 'http://3.39.224.161/upload_image'

# GET 요청 보내기
response = requests.get(url)

# 응답 결과 확인
if response.status_code == 200:
    data = response.json()
    print("GET 요청에 대한 응답:")
    print(data)
else:
    print("GET 요청 실패. 응답 코드:", response.status_code)
