import allure
import time
from pages.login_page import LoginPage
from config import TEST_EMAIL, TEST_PASSWORD

@allure.epic("OpenCart UI自动化测试")
@allure.feature("登录模块")
class TestLoginUI:
    @allure.story("正向登录")
    @allure.title("TC-UI-LOGIN-001: 登录-正向正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, driver):
        login_page = LoginPage(driver)
        with allure.step("输入账号密码并提交"):
            login_page.navigate()
            login_page.login(TEST_EMAIL, TEST_PASSWORD)
        with allure.step("校验跳转至 account/account"):
            login_page.verify_login_success()

    @allure.story("异常登录")
    @allure.title("TC-UI-LOGIN-002: 登录-错误密码")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        err_msg = login_page.login_with_wrong_pwd(TEST_EMAIL, "wrong123")
        # ✅ P0 修复：只认凭证错误，不再把"账号被锁"当成通过
        assert "No match" in err_msg, f"期望凭证错误，实际: {err_msg}"

    @allure.story("异常登录")
    @allure.title("TC-UI-LOGIN-003: 登录-不存在邮箱")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_nonexist_email(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        err_msg = login_page.login_with_wrong_pwd("notexist@test.com", "123456")
        # ✅ P0 修复：同上
        assert "No match" in err_msg, f"期望凭证错误，实际: {err_msg}"

    @allure.story("字段校验")
    @allure.title("TC-UI-LOGIN-004: 登录-邮箱为空")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_email(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        # 替换原来page.fill，调用页面封装方法
        login_page.input_text(login_page.email_input, "")
        login_page.input_text(login_page.password_input, TEST_PASSWORD)
        login_page.click(login_page.login_btn)
        driver.implicitly_wait(1)
        # ✅ P1 修复：用 get_login_error()，不再抓 body 全文
        err = login_page.get_login_error()
        assert ("E-Mail Address" in err) or ("No match" in err), \
            f"空邮箱未触发任何校验，实际: {err}"

    @allure.story("字段校验")
    @allure.title("TC-UI-LOGIN-005: 登录-密码为空")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_password(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        login_page.input_text(login_page.email_input, TEST_EMAIL)
        login_page.input_text(login_page.password_input, "")
        login_page.click(login_page.login_btn)
        driver.implicitly_wait(1)
        err = login_page.get_login_error()
        assert ("Password" in err) or ("No match" in err), \
            f"空密码未触发任何校验，实际: {err}"

    @allure.story("安全测试")
    @allure.title("TC-UI-LOGIN-006: 登录-SQL注入防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_sql_injection(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        login_page.input_text(login_page.email_input, "' OR '1'='1' --")
        login_page.input_text(login_page.password_input, "任意")
        login_page.click(login_page.login_btn)
        driver.implicitly_wait(3)
        with allure.step("断言1：未进入已登录路由"):
            route = driver.execute_script("return new URLSearchParams(window.location.search).get('route')")
            assert route != "account/account", f"SQL 注入绕过登录！route={route}"
        with allure.step("断言2：未泄露数据库报错"):
            body = driver.find_element("tag name", "body").text.lower()
            for leak in ("sql syntax", "mysqli", "traceback"):
                assert leak not in body, f"敏感信息泄露: {leak}"

    @allure.story("性能")
    @allure.title("TC-UI-LOGIN-007: 登录-端到端感知耗时")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("口径：含填表、提交、等待页面加载，非接口响应时间")
    def test_login_response_time(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        start = time.perf_counter()
        login_page.login(TEST_EMAIL, TEST_PASSWORD)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 15000, f"端到端耗时 {elapsed:.0f}ms 超过 15000ms"