import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
RIOT_API_URL = "https://na1.api.riotgames.com/lol/static-data/v3/champions"

def get_champion_data():
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }
    response = requests.get(RIOT_API_URL, headers=headers)

    if response.status_code == 200:
        return response.json()  # 챔피언 데이터 반환
    else:
        print("Failed to fetch champion data:", response.status_code)
        return None
