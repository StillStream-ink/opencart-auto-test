import re
from playwright.sync_api import Page
from pages.base_page import BasePage
from config import BASE_URL


class RegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{BASE_URL}/index.php?route=account/register"

        self.firstname_input = page.locator("#input-firstname")
        self.lastname_input = page.locator("#input-lastname")
        self.email_input = page.locator("#input-email")
        self.password_input = page.locator("#input-password")
        self.privacy_checkbox = page.locator("input[name='agree']")
        self.continue_btn = page.get_by_role("button", name="Continue")
        self.success_title = page.locator("#content h1")
        self.alert_error = page.locator(".alert-danger")

    def navigate(self):
        self.page.goto(self.url, wait_until="networkidle")
        return self

    def register(self, firstname: str, lastname: str, email: str, password: str, agree: bool = True):
        self.fill_firstname(firstname)
        self.fill_lastname(lastname)
        self.fill_email(email)
        self.fill_password(password)
        if agree:
            self.check_privacy()
        self.click_continue()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        return self

    def get_success_title(self) -> str:
        return self.success_title.text_content() or ""

    # ========== 通用错误提取 ==========
    def _get_field_error(self, field_id: str, keyword: str) -> str:
        """
        通用字段错误提取：
        1. 先找 input 旁的 .text-danger
        2. 再遍历所有 .text-danger 匹配 keyword
        3. 再找 .alert-danger
        4. 最后正则匹配整个 body
        """
        loc = self.page.locator(f"#{field_id} ~ .text-danger")
        if loc.count() > 0 and loc.first.is_visible():
            return loc.first.text_content().strip()

        for el in self.page.locator(".text-danger").all():
            text = el.text_content().strip()
            if keyword in text:
                return text

        alert = self.page.locator(f".alert-danger:has-text('{keyword}')")
        if alert.count() > 0:
            return alert.first.text_content().strip()

        body = self.page.locator("body").inner_text()
        match = re.search(rf'{keyword}[^!]*!?', body)
        return match.group(0) if match else ""

    def get_firstname_error(self) -> str:
        return self._get_field_error("input-firstname", "First Name")

    def get_email_error(self) -> str:
        return self._get_field_error("input-email", "E-Mail")

    def get_password_error(self) -> str:
        return self._get_field_error("input-password", "Password")

    def get_alert_error(self) -> str:
        return self.alert_error.text_content() or ""

    # ========== 页面操作封装 ==========
    def fill_firstname(self, value: str):
        self.input_text(self.firstname_input, value)

    def fill_lastname(self, value: str):
        self.input_text(self.lastname_input, value)

    def fill_email(self, value: str):
        self.input_text(self.email_input, value)

    def fill_password(self, value: str):
        self.input_text(self.password_input, value)

    def check_privacy(self):
        self.privacy_checkbox.check()

    def click_continue(self):
        self.click(self.continue_btn)