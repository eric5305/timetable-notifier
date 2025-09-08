import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
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
    # 셀레니움 웹 드라이버 설정 (클라우드 환경용)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # ⭐️ 여기가 핵심! 사람인 척하는 User-Agent 추가
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30) # 페이지 로딩 타임아웃을 30초로 설정

    try:
        # 컴시간 알리미 사이트 접속
        driver.get("http://comci.kr:4082/st")
        time.sleep(2) # 안정성을 위해 대기 시간 증가

        # 학교 검색 및 선택
        driver.find_element(By.ID, "sc").send_keys(SCHOOL_NAME)
        driver.find_element(By.ID, "schulbtn").click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="school_ra"]/table/tbody/tr[1]/td[1]/a').click()
        time.sleep(2)

        # 학년 및 반 선택
        Select(driver.find_element(By.ID, "학년")).select_by_visible_text(GRADE)
        Select(driver.find_element(By.ID, "반")).select_by_visible_text(CLASS_NUM)
        driver.find_element(By.ID, "bt").click()
        time.sleep(3) # 시간표 로딩을 위해 대기 시간 증가

        # 시간표 정보 파싱
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

        return timetable_text if timetable_text else "오늘 시간표 정보가 없어요."

    except Exception as e:
        return f"시간표 가져오기 오류: {e}"
    finally:
        driver.quit()

def send_notification(message):
    try:
        title_header = f"📢 {GRADE}학년 {CLASS_NUM}반 오늘의 시간표".encode('utf-8')

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": title_header}
        )
        print("알림을 성공적으로 보냈습니다.")
    except Exception as e:
        print(f"알림 보내기 실패: {e}")

# --- 메인 코드 실행 ---
if __name__ == "__main__":
    today_timetable = get_timetable()
    send_notification(today_timetable)
