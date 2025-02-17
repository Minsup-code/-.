import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from config.config import SELENIUM_HEADLESS
from config.secrets import MEXC_LOGIN_EMAIL, MEXC_LOGIN_PASSWORD

class BrowserStealth:
    """
    undetected-chromedriver 기반 Selenium 스텔스 브라우저 세팅.
    MEXC 로그인 기능 포함.
    """

    def init_driver(self):
        options = Options()
        if SELENIUM_HEADLESS:
            options.add_argument("--headless")

        # 추가 옵션 설정 
        # options.add_argument("--disable-gpu")

        driver = uc.Chrome(options=options)
        driver.maximize_window()
        return driver

    def login_mexc(self, driver):
        """
        MEXC 로그인 (이메일/비밀번호).
        MEXC 사이트 HTML 변경 시 업데이트 필요
        """
        logger.info("[BrowserStealth] MEXC 로그인 페이지 접속 중...")
        driver.get("https://www.mexc.com/ko-KR/login")
        time.sleep(2)
        

        try:
            #이메일 입력 필드를 찾는 코드. 사이트가 로딩되는 시간을 위해 2초의 딜레이를 넣었습니다.
            email_input = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH,
                '//*[@id="emailInputwwwmexccom"]'))
            )
            
            email_input.clear()
            email_input.send_keys(MEXC_LOGIN_EMAIL)
            logger.info("[BrowserStealth] 이메일 입력 완료.")
        
        except Exception as e:
            logger.error(f"[BrowserStealth] 이메일 입력 필드를 찾을 수 없음: {e}")

            
            #비밀번호 입력 필드를 찾는 코드. 사이트는 이미 로딩되었기에 1초만 추가했습니다.
            pw_input = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH,
                 '//*[@id="passwordInput"]'))
            )

            # 기존 값 지우기
            pw_input.clear()

            # 비밀번호 입력
            MEXC_LOGIN_PASSWORD = "your_password"  # 여기에 비밀번호 설정
            pw_input.send_keys(MEXC_LOGIN_PASSWORD)

            # 입력 후 대기
            time.sleep(1)

        except Exception as e:
            print("비밀번호 입력 중 오류 발생:", e)


            #로그인 버튼 찾는 코드 
            # 텍스트 "로그인"을 포함하는 버튼 (한글 페이지 기준)
            login_btn = driver.find_element(
                By.XPATH,
                '//*[@id="login"]/div[5]/div/div/div/div/div/div/div[2]/button'
            )
            login_btn.submit()
            logger.info("[BrowserStealth] 로그인 버튼 클릭 완료.")

            # 로그인 후 대기 (10초)
            time.sleep(10)

            # 2FA(OTP 또는 이메일 인증) 수동 입력 대기
            logger.info("[BrowserStealth] 로그인 시도 중... 2FA 입력이 필요하면 브라우저에서 직접 처리하세요.")
            input("[BrowserStealth] OTP 또는 이메일 인증을 완료한 후 엔터를 눌러 주세요...")

        except Exception as e:
            logger.error(f"[BrowserStealth] 로그인 버튼을 찾을 수 없음: {e}")
            return False  # 로그인 실패 처리


            # 로그인 완료 확인(예시): 특정 엘리먼트 존재 여부, URL 확인 등
            current_url = driver.current_url
            if "login" not in current_url:
                logger.info("[BrowserStealth] 로그인 성공으로 간주.")
            else:
                logger.warning("[BrowserStealth] 여전히 /login 페이지 -> 로그인 실패 가능성.")

        except Exception as e:
            logger.error(f"[BrowserStealth] 로그인 오류: {e}")
            # 필요 시 프로그램 종료 or 재시도
            time.sleep(3)
