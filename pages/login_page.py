from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = "http://127.0.0.1/opencart/index.php?route=account/login"

        self.email_input = "#input-email"
        self.password_input = "#input-password"
        self.login_btn = "button:has-text('Login')"

    def navigate(self):
        self.page.goto(self.url, wait_until="load")
        self.page.wait_for_selector("#form-login", state="visible", timeout=12000)
        self.page.wait_for_timeout(1500)
        return self

    def login(self, username: str, password: str):
        email_loc = self.page.locator(self.email_input)
        email_loc.wait_for(state="visible", timeout=10000)
        email_loc.click()
        email_loc.clear()
        email_loc.type(username, delay=50)
        self.page.wait_for_timeout(500)

        pwd_loc = self.page.locator(self.password_input)
        pwd_loc.wait_for(state="visible", timeout=10000)
        pwd_loc.click()
        pwd_loc.clear()
        pwd_loc.type(password, delay=50)
        self.page.wait_for_timeout(500)

        actual_email = email_loc.input_value()
        actual_pwd = pwd_loc.input_value()
        print(f"\n【调试】实际输入邮箱: {actual_email}")
        print(f"【调试】实际输入密码: {actual_pwd}\n")

        login_button = self.page.locator(self.login_btn)
        login_button.wait_for(state="visible", timeout=10000)
        login_button.click()

        self.page.wait_for_load_state("networkidle", timeout=15000)
        self.page.wait_for_timeout(2000)
        print(f"\n【登录后URL】{self.page.url}\n")

        # 登录成功后设置语言cookie
        self.page.context.add_cookies([
            {"name": "language", "value": "en", "domain": "127.0.0.1", "path": "/"}
        ])
        self.page.reload(wait_until="networkidle")
        self.page.wait_for_timeout(1000)

        return self

    def login_with_wrong_pwd(self, username: str, password: str) -> str:
        email_loc = self.page.locator(self.email_input)
        email_loc.click()
        email_loc.clear()
        email_loc.type(username, delay=50)

        pwd_loc = self.page.locator(self.password_input)
        pwd_loc.click()
        pwd_loc.clear()
        pwd_loc.type(password, delay=50)

        self.page.wait_for_timeout(500)
        self.page.locator(self.login_btn).click()

        self.page.wait_for_load_state("networkidle", timeout=8000)
        warning_loc = self.page.locator("text=Warning:")
        warning_loc.wait_for(state="visible", timeout=8000)
        return warning_loc.text_content().strip()

    def verify_login_success(self):
        route_val = self.page.evaluate("()=>new URLSearchParams(window.location.search).get('route')")
        assert route_val == "account/account", f"登录校验失败！预期route=account/account，实际route={route_val}，当前url={self.page.url}"
        return self