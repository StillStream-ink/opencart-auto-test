import allure
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 日志基础配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElementClickError(Exception):
    """元素点击失败异常"""
    pass

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 全局显式等待10秒

    def wait_element_visible(self, locator, timeout: int = 12):
        """等待元素可见，单位秒，替代playwright state=visible"""
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def click(self, locator, timeout=12, retry_count=2):
        """点击元素，自带失败重试（和原来playwright逻辑一致）"""
        for attempt in range(retry_count):
            try:
                self.wait_element_visible(locator, timeout)
                element = self.wait.until(EC.element_to_be_clickable(locator))
                element.click()
                logger.info("点击成功")
                return
            except Exception as err:
                logger.warning(f"点击失败，第{attempt + 1}次重试: {err}")
                self.driver.implicitly_wait(1)
        raise ElementClickError(f"元素多次点击失败: {locator}")

    def input_text(self, locator, text: str, timeout=12):
        """输入文本：先清空再输入"""
        self.wait_element_visible(locator, timeout)
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def scroll_to_bottom(self):
        """滚动到页面底部（适配OpenCart结算长页面）"""
        self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'})")
        self.driver.implicitly_wait(0.8)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self.driver.implicitly_wait(0.5)

    def wait_network_idle(self, wait_sec=2):
        """Selenium模拟等待页面加载完成，JS休眠等待ajax请求结束"""
        self.driver.implicitly_wait(wait_sec)

    def goto(self, url: str, timeout=15):
        """访问页面，等待加载"""
        self.driver.get(url)
        self.wait_network_idle()

    def find_element(self, locator):
        """显式等待查找元素"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def capture_screenshot(self, name="失败截图"):
        """截图并挂载到Allure报告"""
        screenshot_bytes = self.driver.get_screenshot_as_png()
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)