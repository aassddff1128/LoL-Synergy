from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import firebase_admin
from firebase_admin import credentials, firestore
from selenium.webdriver.chrome.service import Service

# Firebase 초기화
cred = credentials.Certificate("D:/test/pythonProject1/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# ChromeDriver 경로 설정
driver_path = 'D:/test/pythonProject1/chromedriver-win64/chromedriver-win64/chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Riot Universe 챔피언 목록 페이지로 이동 (최초 페이지 접근만 자동으로 수행)
url = 'https://universe.leagueoflegends.com/ko_KR/champions/'
driver.get(url)

# 페이지 접근 로그
print("페이지에 접근했습니다. 이제 수동으로 조작하세요.")


def save_champion_to_firestore(region_name):
    try:
        # itemContent_3olR 클래스가 있는지 확인
        item_content_elements = driver.find_elements(By.CLASS_NAME, 'itemContent_3olR')

        if item_content_elements:
            print(f"itemContent_3olR 클래스가 {len(item_content_elements)}개 존재합니다.")

            for element in item_content_elements:
                try:
                    # copy_xxN7 클래스 하위의 h1 요소 찾기
                    h1_element = element.find_element(By.CSS_SELECTOR, 'div.copy_xxN7 h1')
                    champion_name = h1_element.text.strip()
                    print(f"h1 챔피언 이름: {champion_name}")

                    # Firebase Firestore에 지역명과 챔피언 이름 저장
                    champ_data = {
                        'region': region_name,
                        'champion_name': champion_name
                    }

                    # Firestore에 저장 (컬렉션: champions, 문서 ID: 챔피언 이름)
                    doc_ref = db.collection('champions').document(champion_name)
                    doc_ref.set(champ_data)
                    print(f"'{champion_name}' 챔피언이 '{region_name}' 지역에 저장되었습니다.")

                    # Firestore에서 저장된 데이터 다시 가져오기
                    fetch_champion_from_firestore(champion_name)

                except Exception as e:
                    print(f"copy_xxN7 하위 h1 요소를 찾는 중 오류 발생: {e}")
        else:
            print("itemContent_3olR 클래스를 찾지 못했습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")


# Firestore에서 챔피언 데이터를 다시 가져와서 로그로 출력하는 함수
def fetch_champion_from_firestore(champion_name):
    try:
        # Firestore에서 챔피언 데이터 가져오기
        doc_ref = db.collection('champions').document(champion_name)
        doc = doc_ref.get()

        if doc.exists:
            champion_data = doc.to_dict()
            print(f"저장된 데이터: {champion_data}")
        else:
            print(f"{champion_name}에 대한 데이터가 Firestore에 없습니다.")

    except Exception as e:
        print(f"데이터를 가져오는 중 오류 발생: {e}")


while True:
    # 사용자가 수동으로 이동한 후 해당 지역명으로 작업 시작
    region_name = input("지역명을 입력하세요 (종료하려면 'exit' 입력): ")

    if region_name.lower() == 'exit':
        print("작업을 종료합니다.")
        break

    # 지역 페이지에서 copy_xxN7 하위의 h1 값을 로그로 출력하고 Firestore에 저장 및 데이터 가져오기
    save_champion_to_firestore(region_name)

    # 한 지역 작업 완료 후 사용자에게 수동 작업 지시
    print("작업이 완료되었습니다. 다음 페이지로 이동한 후 Enter를 눌러주세요.")
    input("다음 작업을 위해 이동한 후 Enter를 누르세요.")

# 브라우저 종료
driver.quit()
print("작업이 완료되었습니다. 브라우저를 종료합니다.")
