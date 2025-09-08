import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import datetime

# --- ‼️ 여기 정보는 수정할 수 있습니다 ‼️ ---
NTFY_TOPIC = os.environ.get('NTFY_TOPIC')
SCHOOL_NAME = "칠곡중학교"
GRADE = "2"
CLASS_NUM = "1"
# -----------------------------------------

def get_timetable():
    print(">>> get_timetable 함수 시작")
    # 셀레니움 웹 드라이버 설정 (클라우드 환경용)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    print(">>> 웹 드라이버 옵션 설정 완료")

    driver = webdriver.Chrome(options=options)
    print(">>> 웹 드라이버 실행 완료")

    try:
        # 컴시간 알리미 사이트 접속
        print(">>> 컴시간 사이트 접속 시도...")
        driver.get("http://comci.kr:4082/st")
        print(">>> 사이트 접속 성공!")
        time.sleep(1)

        # 학교 검색 및 선택
        print(">>> 학교 검색 시작...")
        driver.find_element(By.ID, "sc").send_keys(SCHOOL_NAME)
        driver.find_element(By.ID, "schulbtn").click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="school_ra"]/table/tbody/tr[1]/td[1]/a').click()
        time.sleep(1)
        print(">>> 학교 선택 완료!")

        # 학년 및 반 선택
        print(">>> 학년/반 선택 시작...")
        Select(driver.find_element(By.ID, "학년")).select_by_visible_text(GRADE)
        Select(driver.find_element(By.ID, "반")).select_by_visible_text(CLASS_NUM)
        driver.find_element(By.ID, "bt").click()
        time.sleep(2)
        print(">>> 시간표 보기 클릭 완료!")

        # 시간표 정보 파싱
        print(">>> 시간표 파싱 시작...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        today_weekday = datetime.datetime.today().weekday() + 1

        if today_weekday > 5:
            return "오늘은 주말입니다! 😊"

        timetable_text = ""
        for period in range(1, 8):
            try:
                subject = soup.select_one(f'#hour-content-container > table > tbody > tr:nth-of-type({period}) > td:nth-of-type({today_weekday})').get_text(strip=True)
                if subject:
                    timetable_text += f"{period}교시: {subject}\n"
            except AttributeError:
                continue

        print(">>> 시간표 파싱 완료!")
        return timetable_text if timetable_text else "오늘 시간표 정보가 없어요."

    except Exception as e:
        error_message = f"시간표 가져오기 오류: {e}"
        print(f">>> 오류 발생: {error_message}")
        return error_message
    finally:
        print(">>> 드라이버 종료 시도...")
        driver.quit()
        print(">>> 드라이버 종료 완료.")

def send_notification(message):
    print(">>> send_notification 함수 시작")
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": f"📢 {GRADE}학년 {CLASS_NUM}반 오늘의 시간표"}
        )
        print(">>> 알림을 성공적으로 보냈습니다.")
    except Exception as e:
        print(f">>> 알림 보내기 실패: {e}")

# --- 메인 코드 실행 ---
if __name__ == "__main__":
    print("--- 스크립트 실행 시작 ---")
    today_timetable = get_timetable()
    send_notification(today_timetable)
    print("--- 스크립트 실행 완료 ---")
