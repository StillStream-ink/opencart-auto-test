import allure
import time
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from config import TEST_EMAIL, TEST_PASSWORD


@allure.epic("OpenCart UI自动化测试")
@allure.feature("登录模块")
class TestLoginUI:
    @allure.story("正向登录")
    @allure.title("TC‑UI‑LOGIN‑001: 登录‑正向正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页面，输入账号密码并提交"):
            login_page.navigate()
            login_page.login(TEST_EMAIL, TEST_PASSWORD)
        with allure.step("校验成功跳转 account/account 账户主页"):
            login_page.verify_login_success()

    @allure.story("异常登录")
    @allure.title("TC‑UI‑LOGIN‑002: 登录‑错误密码")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页，输入正确邮箱、错误密码提交"):
            login_page.navigate()
            login_page.login_with_wrong_pwd(TEST_EMAIL, "wrong123")
        with allure.step("校验登录失败，仍然停留在登录页面"):
            login_page.verify_login_fail()

    @allure.story("异常登录")
    @allure.title("TC‑UI‑LOGIN‑003: 登录‑不存在邮箱")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_nonexist_email(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页，输入不存在邮箱+密码提交"):
            login_page.navigate()
            login_page.login_with_wrong_pwd("notexist@test.com", "123456")
        with allure.step("校验登录失败，仍然停留在登录页面"):
            login_page.verify_login_fail()

    @allure.story("字段校验")
    @allure.title("TC‑UI‑LOGIN‑004: 登录‑邮箱为空")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_email(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页，邮箱留空，填写密码，回车提交"):
            login_page.navigate()
            login_page.input_text(login_page.input_email, "")
            login_page.input_text(login_page.input_password, TEST_PASSWORD)
            login_page.press_enter(login_page.input_password)
        with allure.step("校验登录失败，仍然停留在登录页面"):
            login_page.verify_login_fail()

    @allure.story("字段校验")
    @allure.title("TC‑UI‑LOGIN‑005: 登录‑密码为空")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_password(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页，填写邮箱，密码留空，回车提交"):
            login_page.navigate()
            login_page.input_text(login_page.input_email, TEST_EMAIL)
            login_page.input_text(login_page.input_password, "")
            login_page.press_enter(login_page.input_password)
        with allure.step("校验登录失败，仍然停留在登录页面"):
            login_page.verify_login_fail()

    @allure.story("安全测试")
    @allure.title("TC‑UI‑LOGIN‑006: 登录‑SQL注入防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_sql_injection(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页面，输入SQL注入payload提交"):
            login_page.navigate()
            login_page.input_text(login_page.input_email, "' OR '1'='1' --")
            login_page.input_text(login_page.input_password, "任意")
            login_page.press_enter(login_page.input_password)
        with allure.step("断言1：没有跳转到账户主页，未成功登录"):
            route = driver.execute_script("return new URLSearchParams(window.location.search).get('route')")
            assert route != "account/account", f"SQL 注入绕过登录！route={route}"
        with allure.step("断言2：页面不存在数据库报错敏感信息"):
            body_text = login_page.find_element((By.TAG_NAME, "body")).text.lower()
            for leak in ("sql syntax", "mysqli", "traceback"):
                assert leak not in body_text, f"敏感信息泄露: {leak}"

    @allure.story("性能")
    @allure.title("TC‑UI‑LOGIN‑007: 登录‑端到端感知耗时")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("口径：含填表、提交、等待页面加载，非接口响应时间")
    def test_login_response_time(self, driver):
        login_page = LoginPage(driver)
        with allure.step("访问登录页面，记录登录操作耗时"):
            login_page.navigate()
            start = time.perf_counter()
            login_page.login(TEST_EMAIL, TEST_PASSWORD)
            elapsed = (time.perf_counter() - start) * 1000
        with allure.step("断言端到端耗时小于15000ms"):
            assert elapsed < 15000, f"端到端耗时 {elapsed:.0f}ms 超过 15000ms"