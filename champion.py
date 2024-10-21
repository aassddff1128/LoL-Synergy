import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
cred = credentials.Certificate("D:/test/pythonProject1/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 데이터 파일 경로
data_file_path = "D:/test/pythonProject1/champion_data.txt"


def save_champions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_champion = None

    for line in lines:
        line = line.strip()
        if line == "":  # 빈 줄은 무시
            continue

        # 챔피언 이름 확인
        if current_champion is None:
            current_champion = line.split('\t')[0]  # 챔피언 이름만 가져옴
            print(f"챔피언: {current_champion}의 데이터를 저장합니다.")
            doc_ref = db.collection('champions').document(current_champion)
            # 챔피언 문서가 존재하는지 확인
            if not doc_ref.get().exists:
                print(f"'{current_champion}' 문서가 존재하지 않습니다.")
                current_champion = None  # 문서가 존재하지 않으면 챔피언 이름 초기화
                continue
        else:
            # 관련 챔피언 및 점수 읽기 (탭으로 분리)
            try:
                parts = line.split('\t')
                if len(parts) != 2:
                    raise ValueError  # 형식이 올바르지 않으면 오류 발생

                name, score = parts  # 각각 이름과 점수로 분리
                score = int(score.strip())  # 점수는 정수형으로 변환
                name = name.strip()  # 이름 앞뒤 공백 제거

                # Firestore에서 relationships 가져오기
                doc = doc_ref.get()
                if doc.exists:
                    relationships = doc.to_dict().get('relationships', [])
                    # 기존 데이터 업데이트
                    for relation in relationships:
                        if relation['name'] == name:
                            relation['score'] = score  # 점수 업데이트
                            break
                    else:
                        # 새로운 데이터 추가
                        relationships.append({"name": name, "score": score})

                    # 업데이트된 relationships 저장
                    doc_ref.update({'relationships': relationships})
                else:
                    print(f"'{current_champion}' 문서가 존재하지 않습니다.")

                print(f"'{name}' 저장 완료: 점수 {score}")

            except ValueError:
                print(f"'{line}'는 유효하지 않은 형식입니다. (형식: 이름\t점수)")

            # 현재 챔피언을 저장한 후 다음 챔피언으로 이동
            current_champion = None


# 실행
save_champions_from_file(data_file_path)
