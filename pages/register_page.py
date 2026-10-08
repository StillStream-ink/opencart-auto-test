import re
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import BASE_URL


class RegisterPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{BASE_URL}/index.php?route=account/register"
        self.firstname_input = (By.ID, "input-firstname")
        self.lastname_input = (By.ID, "input-lastname")
        self.email_input = (By.ID, "input-email")
        self.password_input = (By.ID, "input-password")
        self.privacy_checkbox = (By.CSS_SELECTOR, "input[name='agree']")
        self.continue_btn = (By.XPATH, "//button[normalize-space()='Continue']")
        self.success_title = (By.CSS_SELECTOR, "#content h1")
        self.alert_error = (By.CSS_SELECTOR, ".alert-danger")

    def navigate(self):
        self.goto(self.url)
        self.wait_network_idle(wait_sec=2)
        return self

    def register(self, firstname: str, lastname: str, email: str, password: str, agree: bool = True):
        self.fill_firstname(firstname)
        self.fill_lastname(lastname)
        self.fill_email(email)
        self.fill_password(password)
        if agree:
            self.check_privacy()
        self.click_continue()
        self.wait_network_idle(wait_sec=2)
        return self

    def get_success_title(self) -> str:
        elem = self.find_element(self.success_title)
        return elem.text.strip()

    def _get_field_error(self, field_id: str, keyword: str) -> str:
        """
        通用字段错误提取：
        1. 先找 input 旁的 .text-danger
        2. 再遍历所有 .text-danger 匹配 keyword
        3. 再找 .alert-danger
        4. 最后正则匹配整个 body
        """
        loc_field_err = (By.CSS_SELECTOR, f"#{field_id} ~ .text-danger")
        try:
            elem = self.find_element(loc_field_err)
            txt = elem.text.strip()
            if keyword in txt:
                return txt
        except Exception:
            pass

        danger_elems = self.driver.find_elements(By.CSS_SELECTOR, ".text-danger")
        for el in danger_elems:
            t = el.text.strip()
            if keyword in t:
                return t

        try:
            alert_elem = self.find_element(self.alert_error)
            alert_txt = alert_elem.text.strip()
            if keyword in alert_txt:
                return alert_txt
        except Exception:
            pass

        body_text = self.find_element((By.TAG_NAME, "body")).text
        match = re.search(rf'{re.escape(keyword)}[^!]*!?', body_text)
        return match.group(0).strip() if match else ""

    def get_firstname_error(self) -> str:
        return self._get_field_error("input-firstname", "First Name")

    def get_email_error(self) -> str:
        return self._get_field_error("input-email", "E‑Mail")

    def get_password_error(self) -> str:
        return self._get_field_error("input-password", "Password")

    def get_alert_error(self) -> str:
        elem = self.find_element(self.alert_error)
        return elem.text.strip()

    def fill_firstname(self, value: str):
        self.input_text(self.firstname_input, value)

    def fill_lastname(self, value: str):
        self.input_text(self.lastname_input, value)

    def fill_email(self, value: str):
        self.input_text(self.email_input, value)

    def fill_password(self, value: str):
        self.input_text(self.password_input, value)

    def check_privacy(self):
        cb = self.find_element(self.privacy_checkbox)
        if not cb.is_selected():
            cb.click()

    def click_continue(self):
        self.click(self.continue_btn)