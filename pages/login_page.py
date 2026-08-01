from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "http://localhost/opencart/index.php?route=account/login"
        self.email_input = "#input-email"
        self.password_input = "#input-password"
        self.login_button = "button[type='submit']"

    def navigate(self):
        self.page.goto(self.url, wait_until="networkidle")
        return self

    def login(self, username: str = "mytest203@test.com", password: str = "Open2026"):
        self.page.fill(self.email_input, username)
        self.page.fill(self.password_input, password)
        # 方案一：按 Enter 键提交表单（在密码框上按 Enter）
        self.page.press(self.password_input, "Enter")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(3000)
        return self

    def verify_login_success(self):
        """验证登录成功"""
        assert "account/account" in self.page.url, f"登录失败，当前URL: {self.page.url}"
        return self