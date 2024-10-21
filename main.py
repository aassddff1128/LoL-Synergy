from flask import Flask, jsonify, request, render_template
from firebase_config import db, add_champion_tags_to_db  # Firestore 데이터베이스 설정 및 태그 추가 함수
import random
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)  # INFO 레벨의 로그를 콘솔에 출력

random_champion = None  # 전역 변수로 랜덤 챔피언을 저장

def calculate_champion_similarity(champ1, champ2):
    # 두 챔피언이 동일한 경우
    if champ1['champion_name'] == champ2['champion_name']:
        return 100  # 동일 챔피언 간의 점수

    # 챔피언 간의 유사성 점수를 계산하는 로직
    tags1 = set(champ1.get('tags', []))
    tags2 = set(champ2.get('tags', []))
    common_tags = tags1.intersection(tags2)

    # 기본 점수를 설정하여 점수를 보장
    score = len(common_tags) * 10  # 태그당 10점
    if score == 0:
        score = 1  # 태그가 하나도 없는 경우 기본 점수 부여

    return score

def calculate_champion_scores(random_champ, all_champs):
    scores = []
    for champ in all_champs:
        score = calculate_champion_similarity(random_champ, champ)  # 유사성 계산
        scores.append({'name': champ['champion_name'], 'score': score})

    # 점수를 기준으로 정렬하고 등수 매기기
    scores.sort(key=lambda x: x['score'], reverse=True)  # 점수 높은 순으로 정렬
    for rank, champ in enumerate(scores, start=1):
        champ['rank'] = rank  # 각 챔피언에 등수 추가

    return scores

def select_random_champion():
    champs = db.collection('champions').stream()
    champ_list = [champ.to_dict() for champ in champs]  # 제너레이터를 리스트로 변환

    if not champ_list:
        print("No champions found in the database.")
        return None

    random_champ = random.choice(champ_list)
    scores = calculate_champion_scores(random_champ, champ_list)  # 점수 계산
    app.logger.info(f"Random Champion Selected: {random_champ['champion_name']}")

    return random_champ, scores  # 랜덤 챔피언과 모든 챔피언 점수 반환

@app.route('/')
def index():
    return render_template('index.html')  # index.html 매핑

@app.route('/api/random_champion', methods=['GET'])
def get_random_champion():
    global random_champion
    random_champion, scores = select_random_champion()

    if not random_champion:
        return jsonify({'error': 'No champions available'}), 404

    return jsonify({
        'random_champion': random_champion['champion_name'],
        'scores': scores  # 점수 정보도 반환
    }), 200

@app.route('/api/similarity', methods=['POST'])
def similarity():
    data = request.get_json()
    user_champion_name = data.get('champion')

    if not random_champion:
        return jsonify({'error': 'Random champion is not set'}), 400

    user_champ_doc = db.collection('champions').where('champion_name', '==', user_champion_name).get()

    if not user_champ_doc:
        return jsonify({'error': 'Champion not found'}), 404

    user_champ_data = user_champ_doc[0].to_dict()

    # 가렌의 챔피언 데이터 가져오기
    garen_champ_doc = db.collection('champions').where('champion_name', '==', '가렌').get()
    if not garen_champ_doc:
        app.logger.error('Garen not found in champions')
        return jsonify({'error': 'Garen not found in champions'}), 404

    garen_champ_data = garen_champ_doc[0].to_dict()
    app.logger.info(f"Garen data: {garen_champ_data}")  # 가렌 데이터 로그 추가

    # 가렌과 사용자 챔피언 간의 유사성 점수 계산
    garen_score = calculate_champion_similarity(garen_champ_data, user_champ_data)
    app.logger.info(f"Garen vs {user_champion_name} Score: {garen_score}")  # 점수 계산 로그 추가

    # 전체 챔피언과 점수 계산
    all_champs = [user_champ_data] + [champ.to_dict() for champ in db.collection('champions').stream()]
    all_scores = calculate_champion_scores(random_champion, all_champs)

    user_score_info = next((item for item in all_scores if item['name'] == user_champion_name), None)

    if user_score_info:
        app.logger.info(f"Champion: {user_champion_name}, Score: {user_score_info['score']}, Rank: {user_score_info['rank']}")
        return jsonify({
            'random_champion': random_champion['champion_name'],
            'user_champion': user_champion_name,
            'user_score': user_score_info['score'],
            'user_rank': user_score_info['rank']
        }), 200
    else:
        app.logger.error('User champion score not found')
        return jsonify({'error': 'User champion score not found'}), 404

@app.route('/api/champion_search', methods=['GET'])
def champion_search():
    query = request.args.get('q', '').lower()

    champ_docs = db.collection('champions').stream()
    matched_champions = []

    for champ in champ_docs:
        champ_data = champ.to_dict()
        if 'champion_name' in champ_data:
            if query in champ_data['champion_name'].lower():
                matched_champions.append(champ_data['champion_name'])

    return jsonify(matched_champions), 200

if __name__ == '__main__':
    add_champion_tags_to_db()  # 챔피언 태그를 데이터베이스에 추가
    app.run(debug=True)  # Flask 애플리케이션 실행
