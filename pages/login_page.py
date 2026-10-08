from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from config import BASE_URL, BASE_DOMAIN

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{BASE_URL}/index.php?route=account/login"
        # Selenium定位器：元组 (By.xxx, 选择器)
        self.email_input = (By.ID, "input-email")
        self.password_input = (By.ID, "input-password")
        self.login_btn = (By.CSS_SELECTOR, "button:has-text('Login')")
        self.warning_alert = (By.CSS_SELECTOR, ".alert-danger")
        self.text_danger = (By.CSS_SELECTOR, ".text-danger")

    def navigate(self):
        self.goto(self.url)
        self.wait_element_visible((By.CSS_SELECTOR, "#form-login"), timeout=12)
        return self

    def _fill_and_submit(self, username: str, password: str):
        """公共方法：填表 + 提交（供 login 和 login_with_wrong_pwd 复用）"""
        # 输入账号
        self.input_text(self.email_input, username)
        # 输入密码
        self.input_text(self.password_input, password)
        # 点击登录按钮
        self.click(self.login_btn)
        # 等待网络空闲，模拟Playwright networkidle
        self.wait_network_idle(wait_sec=2)

    def login(self, username: str, password: str):
        self._fill_and_submit(username, password)
        self.driver.implicitly_wait(2)
        # 设置cookie：Selenium添加cookie前必须先访问对应域名页面
        self.driver.add_cookie({"name": "language", "value": "en", "domain": BASE_DOMAIN, "path": "/"})
        self.driver.refresh()
        self.wait_network_idle(wait_sec=1)
        return self

    def login_with_wrong_pwd(self, username: str, password: str) -> str:
        self._fill_and_submit(username, password)
        self.wait_element_visible(self.warning_alert, timeout=8)
        return self.find_element(self.warning_alert).text.strip()

    def get_login_error(self) -> str:
        """提取登录页错误文案，保留原来四层降级逻辑"""
        try:
            # 优先找 .alert-danger
            elem = self.find_element(self.warning_alert)
            return elem.text.strip()
        except Exception:
            try:
                elem = self.find_element(self.text_danger)
                return elem.text.strip()
            except Exception:
                # 兜底：页面文本正则匹配Warning
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                import re
                m = re.search(r'Warning:[^\n]*', page_text)
                return m.group(0).strip() if m else ""

    def verify_login_success(self):
        """校验登录成功，读取url参数，判断路由"""
        # JS执行获取url里route参数
        route_val = self.driver.execute_script("return new URLSearchParams(window.location.search).get('route')")
        assert route_val == "account/account", \
            f"登录校验失败！预期route=account/account，实际route={route_val}，当前url={self.driver.current_url}"
        return self