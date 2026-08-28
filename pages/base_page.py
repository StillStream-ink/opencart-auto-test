from playwright.sync_api import Locator, Page
import logging

# 日志基础配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasePage:
    def __init__(self, page: Page):
        self.page: Page = page

    def wait_element_visible(self, locator: Locator, timeout: int = 12000):
        """等待元素可见"""
        locator.wait_for(state="visible", timeout=timeout)

    def click(self, locator: Locator, timeout=12000, retry_count=2):
        """点击元素，自带失败重试"""
        for attempt in range(retry_count):
            try:
                self.wait_element_visible(locator, timeout)
                locator.click()
                logger.info("点击成功")
                return
            except Exception as err:
                logger.warning(f"点击失败，第{attempt+1}次重试: {err}")
                self.page.wait_for_timeout(1000)
        raise Exception("元素多次点击失败")

    def input_text(self, locator: Locator, text: str, timeout=12000):
        """输入文本，先清空"""
        self.wait_element_visible(locator, timeout)
        locator.fill("")
        locator.fill(text)

    def scroll_to_bottom(self):
        """强力滚动到页面底部（适配OpenCart长结算页面）"""
        self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'})")
        self.page.wait_for_timeout(800)
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)

    def wait_network_idle(self, wait_ms=2000):
        """等待网络空闲，等待AJAX加载完成"""
        self.page.wait_for_load_state("networkidle", timeout=wait_ms)

    def goto(self, url: str, timeout=15000):
        self.page.goto(url, timeout=timeout)
        self.page.wait_for_load_state("networkidle")