import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from config.config import (
    ORDER_CLICK_DELAY,
    MAX_ORDER_RETRY,
    MIN_RANDOM_DELAY,
    MAX_RANDOM_DELAY,
    LONG_REST_EVERY_N_ORDERS,
    MIN_LONG_REST_SEC,
    MAX_LONG_REST_SEC
)


class OrderExecutor:
    """
    MEXC 웹페이지에서 포지션 오픈/청산(롱/숏) 버튼을 클릭하는 클래스.
    UI 변경 시 XPATH 수정 필요.
    """

    def __init__(self, driver):
        self.driver = driver
        self.order_count = 0  # 누적 주문 횟수 (안티봇 용)

    def place_market_order(self, side: str, quantity: float) -> bool:
        """
        side: "LONG" or "SHORT"
        quantity: 예) 50, 2
        """
        logger.info(f"[OrderExecutor] 시장가 {side}, 수량={quantity} 주문 시도")
        attempt = 0
        success = False

        while attempt < MAX_ORDER_RETRY and not success:
            attempt += 1
            try:
                # (1) 포지션 오픈 ㅇ
                open_tab = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[1]/div[1]/span[1]'
                )
                open_tab.click()
                time.sleep(0.3)


                # (2) 수량 입력 ㅇ
                open_qty_input = self.driver.find_element(
                    By.ID, 
                    '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[1]/div/div[2]/div/div')

                open_qty_input.clear()
                open_qty_input.send_keys(str(quantity))
                time.sleep(0.2)

                # (3) 롱/숏 버튼 ㅇ
                if side.upper() == "LONG":
                    btn_selector = '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[4]/section/div/div[1]/button[1]'
                else:
                    btn_selector = '//*[@id="mexc_contract_v_open_position"]/div/div[4]/div[4]/section/div/div[1]/button[2]'
                
                btn = WebDriverWait(self.driver, 0.3).until(
                    EC.element_to_be_clickable((By.XPATH, btn_selector))
                )
                btn.click()
                time.sleep(ORDER_CLICK_DELAY)

                logger.info(f"[OrderExecutor] 시장가 {side} {quantity} 주문 완료.")
                success = True

            except Exception as e:
                logger.warning(f"[OrderExecutor] place_market_order() 재시도({attempt}) 실패: {e}")
                time.sleep(1)

        if success:
            self._post_order_delay()  # 안티봇 로직
        return success

    def close_position(self, side: str, quantity: float) -> bool:
        """
        side: "LONG" -> 롱 청산(=매도)
              "SHORT"-> 숏 청산(=매수)
        """
        logger.info(f"[OrderExecutor] {side} 포지션 청산 시도, 수량={quantity}")
        attempt = 0
        success = False

        while attempt < MAX_ORDER_RETRY and not success:
            attempt += 1
            try:
                # (1) '포지션 청산' 탭 ㅇ
                close_tab = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[1]/div[1]/span[2]')

                # (2) 수량 입력 ㅇ 
                close_qty_input = self.driver.find_element(
                    By.ID, 
                    '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div')

                
                close_qty_input.clear()
                close_qty_input.send_keys(str(quantity))
                time.sleep(0.2)

                # (3) 롱 청산/숏 청산 버튼 ㅇ
                if side.upper() == "LONG":
                    btn_selector = '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[1]'
                else:
                    btn_selector = '//*[@id="mexc-web-inspection-futures-exchange-orderForm"]/div[2]/div[2]/div[2]/div/div/div[3]/div[3]/section/div/div[1]/button[2]'
                
                btn = WebDriverWait(self.driver, 0.3).until(
                    EC.element_to_be_clickable((By.XPATH, btn_selector))
                )
                btn.click()
                time.sleep(ORDER_CLICK_DELAY)

                logger.info(f"[OrderExecutor] {side} 청산 {quantity} 완료.")
                success = True

            except Exception as e:
                logger.warning(f"[OrderExecutor] close_position() 재시도({attempt}) 실패: {e}")
                time.sleep(1)

        if success:
            self._post_order_delay()  # 안티봇 로직
        return success

    # -------------------------------------------- 
    # 안티봇 로직
    # --------------------------------------------
    def _post_order_delay(self):
        self.order_count += 1

        # 짧은 딜레이
        rand_sec = random.uniform(MIN_RANDOM_DELAY, MAX_RANDOM_DELAY)
        logger.debug(f"[OrderExecutor] 무작위 딜레이 {rand_sec:.2f}초")
        time.sleep(rand_sec)

        # 일정 횟수마다 긴 휴식
        if self.order_count % LONG_REST_EVERY_N_ORDERS == 0:
            long_rest = random.uniform(MIN_LONG_REST_SEC, MAX_LONG_REST_SEC)
            logger.info(f"[OrderExecutor] 안티봇 장기 휴식 {long_rest:.1f}초")
            time.sleep(long_rest)