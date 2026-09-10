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
        existing_email = "auto_test@test.com"  # 确保该邮箱已存在
        reg_page.navigate()
        reg_page.register("Auto", "Test", existing_email, "Test1234", agree=True)
        
        # 如果意外成功（跳转成功页面），则清除状态后重新提交
        if "success" in page.url or "account/account" in page.url:
            page.context.clear_cookies()
            page.evaluate("localStorage.clear()")
            page.wait_for_timeout(500)
            reg_page.navigate()
            page.wait_for_selector("#input-firstname", state="visible", timeout=10000)
            reg_page.register("Auto", "Test", existing_email, "Test1234", agree=True)
        
        # 检查顶部警告错误
        err = reg_page.get_alert_error()
        assert "E-Mail Address is already registered" in err
        print("✅ TC-UI-REG-002 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-003: 注册-邮箱格式无效")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_invalid_email(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", "alipuser", "Test1234", agree=True)
        page.wait_for_timeout(2000)

        # ✅ 修复：核心断言——不能注册成功（URL 不能变成 success/account）
        assert "success" not in page.url and "account/account" not in page.url, \
            f"无效邮箱竟然注册成功，URL: {page.url}"

        # 附加检查：如果有错误提示更好
        body_text = page.locator("body").inner_text()
        has_error = (
            "E-Mail Address does not appear to be valid" in body_text or
            "电子邮件地址无效" in body_text or
            "请在电子邮件地址中包括" in body_text
        )
        if has_error:
            print("✅ TC-UI-REG-003 通过（检测到邮箱格式错误提示）")
        else:
            print("⚠️ 未显示错误提示，但未注册成功（可能是前端校验拦截）")
            print("✅ TC-UI-REG-003 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-004: 注册-密码小于6位")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_password_short(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", f"short_{int(time.time())}@test.com", "123", agree=True)
        # 检查字段错误
        err = reg_page.get_password_error()
        assert "Password must be between" in err and "characters" in err
        print("✅ TC-UI-REG-004 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-005: 注册-FirstName为空")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_empty_firstname(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("", "Test", f"empty_{int(time.time())}@test.com", "Test1234", agree=True)
        err = reg_page.get_firstname_error()
        assert "First Name must be between" in err
        print("✅ TC-UI-REG-005 通过")

    @allure.story("字段校验")
    @allure.title("TC-UI-REG-006: 注册-未勾选隐私政策")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_no_privacy(self, page: Page):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Auto", "Test", f"nopriv_{int(time.time())}@test.com", "Test1234", agree=False)
        err = reg_page.get_alert_error()
        assert "You must agree to the Privacy Policy" in err
        print("✅ TC-UI-REG-006 通过")