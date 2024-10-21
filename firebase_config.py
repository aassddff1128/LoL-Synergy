import firebase_admin
from firebase_admin import credentials, firestore
from riot_api import get_champion_data  # Riot API에서 챔피언 데이터를 가져오는 함수
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Firebase Admin SDK 초기화
cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))  # 환경 변수에서 서비스 계정 키 파일 경로 가져오기
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 초기화
db = firestore.client()  # Firestore 데이터베이스 클라이언트


def add_champion_tags_to_db():
    champions = get_champion_data()  # API에서 챔피언 데이터 가져오기

    if champions:
        for champ_id, champ_info in champions['data'].items():
            champion_name = champ_info['name']
            tags = champ_info.get('tags', [])  # 태그 필드 가져오기

            # 디버깅을 위한 로그 출력
            print(f"Updating champion: {champion_name} with tags: {tags}")

            # Firestore에 추가 (병합하여 기존 데이터 유지)
            db.collection('champions').document(champion_name).set({
                'tags': tags,
                'region': champ_info.get('region', ''),  # 추가 필드 예시
                'relationships': champ_info.get('relationships', [])  # 추가 필드 예시
            }, merge=True)
        print("Champions tags added to Firestore.")
    else:
        print("No champions data to add.")
