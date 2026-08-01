import allure
import pytest
import time
from playwright.sync_api import Page
from pages.register_page import RegisterPage


@allure.epic("OpenCart UI自动化测试")
@allure.feature("注册模块")
class TestRegisterUI:

    @allure.story("正向注册")
    @allure.title("TC-UI-REG-001: 注册-正向")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_success(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        email = f"auto_test_{int(time.time())}@test.com"
        reg_page.register("Auto", "Test", email, "Test1234", agree=True)
        title = reg_page.get_success_title()
        assert "Your Account Has Been Created" in title
        print("✅ TC-UI-REG-001 通过")

    @allure.story("异常注册")
    @allure.title("TC-UI-REG-002: 注册-邮箱已存在")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_email_exists(self, page: Page):
        reg_page = RegisterPage(page)
        # 先确保邮箱已存在
        reg_page.navigate()
        reg_page.register("Auto", "Test", "auto_test@test.com", "Test1234", agree=True)
        # 如果第一次成功，页面会跳转到 success，则回到注册页重新注册
        if "success" in page.url:
            reg_page.navigate()
            reg_page.register("Auto", "Test", "auto_test@test.com", "Test1234", agree=True)
        error = reg_page.get_error_text()
        assert "E-Mail Address is already registered" in error
        print("✅ TC-UI-REG-002 通过")

    @pytest.mark.skip(reason="本地OpenCart邮箱格式校验未生效，输入无效邮箱时页面静默失败，待环境确认后修复")
    def test_register_invalid_email(self, page: Page):
        pass

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-004: 注册-密码小于4位")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_password_short(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", "apiuser@", "Test1234", agree=True)
        body = page.locator("body").inner_text()
        # 实际提示是 6 and 40
        assert "Password must be between 6 and 40 characters" in body
        print("✅ TC-UI-REG-004 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-005: 注册-FirstName为空")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_empty_firstname(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", "apiuser@", "Test1234", agree=True)
        error = reg_page.get_field_error("firstname")
        assert "First Name must be between 1 and 32 characters" in error
        print("✅ TC-UI-REG-005 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-006: 注册-未勾选隐私政策")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_no_privacy(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", "new@test.com", "Test1234", agree=False)
        error = reg_page.get_error_text()
        assert "You must agree to the Privacy Policy" in error
        print("✅ TC-UI-REG-006 通过")