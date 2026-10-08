from pages.base_page import BasePage
from selenium.webdriver.common.by import By
import allure


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://127.0.0.1/opencart/index.php?route=account/login"
        self.input_email = (By.ID, "input-email")
        self.input_password = (By.ID, "input-password")

    @allure.step("打开登录页面")
    def navigate(self):
        self.goto(self.url)
        return self

    @allure.step("输入账号：{email}，密码：{pwd}，提交登录")
    def login(self, email: str, pwd: str):
        self.input_text(self.input_email, email)
        self.input_text(self.input_password, pwd)
        self.press_enter(self.input_password)
        self.wait_network_idle(3)
        return self

    @allure.step("错误账号密码登录：{email} {pwd}")
    def login_with_wrong_pwd(self, email: str, pwd: str):
        self.input_text(self.input_email, email)
        self.input_text(self.input_password, pwd)
        self.press_enter(self.input_password)
        self.wait_network_idle(3)
        # 返回当前页面路由
        return self.get_current_route()

    def get_current_route(self):
        return self.driver.execute_script("return new URLSearchParams(window.location.search).get('route')")

    @allure.step("校验登录成功，跳转到账户主页")
    def verify_login_success(self):
        route = self.get_current_route()
        assert route == "account/account", f"登录未成功，当前route:{route}"

    @allure.step("校验登录失败，停留在登录页")
    def verify_login_fail(self):
        route = self.get_current_route()
        assert route == "account/login", f"登录不应该成功，但是跳转到route:{route}"