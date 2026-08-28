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

    def get_firstname_error(self) -> str:
        loc = self.page.locator("#input-firstname ~ .text-danger")
        if loc.count() > 0 and loc.first.is_visible():
            return loc.first.text_content().strip()
        for el in self.page.locator(".text-danger").all():
            text = el.text_content().strip()
            if "First Name" in text:
                return text
        alert = self.page.locator(".alert-danger:has-text('First Name')")
        if alert.count() > 0:
            return alert.first.text_content().strip()
        body = self.page.locator("body").inner_text()
        import re
        match = re.search(r'First Name must be between[^!]*!?', body)
        if match:
            return match.group(0)
        return ""

    def get_email_error(self) -> str:
        loc = self.page.locator("#input-email ~ .text-danger")
        if loc.count() > 0 and loc.first.is_visible():
            return loc.first.text_content().strip()
        for el in self.page.locator(".text-danger").all():
            text = el.text_content().strip()
            if "E-Mail" in text:
                return text
        alert = self.page.locator(".alert-danger:has-text('E-Mail')")
        if alert.count() > 0:
            return alert.first.text_content().strip()
        body = self.page.locator("body").inner_text()
        import re
        match = re.search(r'E-Mail Address[^!]*!?', body)
        if match:
            return match.group(0)
        return ""

    def get_password_error(self) -> str:
        # 尝试多种选择器
        loc = self.page.locator("#input-password ~ .text-danger")
        if loc.count() > 0 and loc.first.is_visible():
            return loc.first.text_content().strip()
        for el in self.page.locator(".text-danger").all():
            text = el.text_content().strip()
            if "Password" in text:
                return text
        alert = self.page.locator(".alert-danger:has-text('Password')")
        if alert.count() > 0:
            return alert.first.text_content().strip()
        body = self.page.locator("body").inner_text()
        import re
        match = re.search(r'Password must be between[^!]*!?', body)
        if match:
            return match.group(0)
        return ""

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