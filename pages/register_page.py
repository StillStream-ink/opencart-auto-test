from playwright.sync_api import Page


class RegisterPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "http://localhost/opencart/index.php?route=account/register"

        self.firstname_input = page.locator("#input-firstname")
        self.lastname_input = page.locator("#input-lastname")
        self.email_input = page.locator("#input-email")
        self.password_input = page.locator("#input-password")
        self.privacy_checkbox = page.locator("input[name='agree']")
        self.continue_btn = page.get_by_role("button", name="Continue")

    def navigate(self):
        self.page.goto(self.url, wait_until="networkidle")
        return self

    def register(self, firstname: str, lastname: str, email: str, password: str, agree: bool = True):
        self.firstname_input.fill(firstname)
        self.lastname_input.fill(lastname)
        self.email_input.fill(email)
        self.password_input.fill(password)
        if agree:
            self.privacy_checkbox.check()
        self.continue_btn.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        return self

    def get_success_title(self) -> str:
        return self.page.locator("#content h1").text_content() or ""

    def get_error_text(self) -> str:
        """获取页面任意位置的错误提示（优先顶部警告）"""
        # 尝试获取顶部警告
        alert = self.page.locator(".alert-danger")
        if alert.count() > 0:
            return alert.first.text_content() or ""
        # 否则检查整个页面文本
        return self.page.locator("body").inner_text()

    def get_field_error(self, field: str) -> str:
        """获取字段错误，如果没有则返回空字符串"""
        # 先尝试标准定位
        if field == "firstname":
            locator = self.page.locator("#input-firstname ~ .text-danger")
        elif field == "email":
            locator = self.page.locator("#input-email ~ .text-danger")
        elif field == "password":
            locator = self.page.locator("#input-password ~ .text-danger")
        else:
            return ""
        if locator.count() > 0:
            return locator.first.text_content() or ""
        # 如果没有字段错误，检查页面整体文本
        body = self.page.locator("body").inner_text()
        # 根据常见错误信息返回
        if "E-Mail Address does not appear to be valid" in body:
            return "E-Mail Address does not appear to be valid"
        if "Password must be between 4 and 20 characters" in body:
            return "Password must be between 4 and 20 characters"
        if "First Name must be between 1 and 32 characters" in body:
            return "First Name must be between 1 and 32 characters"
        return ""