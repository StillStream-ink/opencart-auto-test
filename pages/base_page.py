import allure
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import WAIT_TIMEOUT

# 日志基础配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElementClickError(Exception):
    """元素点击失败异常"""
    pass

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)

    def wait_element_visible(self, locator, timeout: int = None):
        """等待元素可见，单位秒"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(locator))

    def click(self, locator, timeout=None, retry_count=2):
        """点击元素，自带失败重试；普通click失败自动降级JS点击，处理遮挡/驱动交互异常"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        for attempt in range(retry_count):
            try:
                self.wait_element_visible(locator, wait_time)
                element = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
                # 新增：滚动到元素，保证在视口内
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                element.click()
                logger.info(f"元素 {locator} 普通点击成功")
                return
            except Exception as err:
                logger.warning(f"普通点击失败，尝试JS兜底点击，第{attempt + 1}次重试: {err}")
                try:
                    element = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(locator))
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info(f"元素 {locator} JS兜底点击成功")
                    return
                except Exception as js_err:
                    logger.warning(f"JS兜底点击同样失败: {js_err}")
        raise ElementClickError(f"元素多次点击失败: {locator}")

    def input_text(self, locator, text: str, timeout=None):
        """输入文本：先等待元素可点击，清空再输入"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        self.wait_element_visible(locator, wait_time)
        element = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
        element.clear()
        element.send_keys(text)
        logger.info(f"向 {locator} 输入内容：{text}")

    @allure.step("对元素按下回车键")
    def press_enter(self, locator, timeout=None):
        """定位元素，按下Enter回车键"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        elem = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
        elem.send_keys(Keys.ENTER)
        logger.info(f"元素 {locator} 按下回车提交")

    def scroll_to_bottom(self):
        """滚动到页面底部（适配OpenCart结算长页面）"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.info("页面滚动至底部")

    def wait_network_idle(self, wait_sec=2):
        """Selenium模拟等待页面加载完成"""
        time.sleep(wait_sec)

    def goto(self, url: str, timeout=None):
        """访问页面，等待加载"""
        self.driver.get(url)
        logger.info(f"访问地址: {url}")
        self.wait_network_idle()

    def find_element(self, locator, timeout=None):
        """显式等待查找单个元素"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(locator))

    def find_elements(self, locator, timeout=None):
        """显式等待查找一组元素"""
        wait_time = timeout if timeout else WAIT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_all_elements_located(locator))

    def get_text(self, locator, timeout=None):
        """获取元素文本"""
        element = self.find_element(locator, timeout)
        return element.text

    def is_element_displayed(self, locator, timeout=None) -> bool:
        """判断元素是否展示"""
        try:
            self.wait_element_visible(locator, timeout)
            return True
        except Exception:
            return False

    def capture_screenshot(self, name="失败截图"):
        """截图并挂载到Allure报告"""
        screenshot_bytes = self.driver.get_screenshot_as_png()
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)