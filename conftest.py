import pytest
import pymysql
import allure
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from config import TEST_EMAIL, TEST_PASSWORD

# ========== 1. Selenium driver fixture（替代原来Playwright page） ==========
@pytest.fixture(scope="function")
def driver():
    options = Options()
    # options.add_argument('--headless=new')   # CI环境打开无头，本地调试注释掉，可以看到浏览器
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

# ========== 2. 已登录 driver Fixture（替换 logged_in_page） ==========
@pytest.fixture
def logged_in_driver(driver):
    """返回已完成登录的driver对象，购物车、结算用例复用"""
    login_page = LoginPage(driver)
    login_page.navigate()
    login_page.login(TEST_EMAIL, TEST_PASSWORD)
    login_page.verify_login_success()
    return driver

# ========== 3. 失败自动截图（Selenium版本，替换page截图） ==========
@pytest.fixture(autouse=True)
def capture_screenshot(request, driver):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_bytes = driver.get_screenshot_as_png()
        allure.attach(
            screenshot_bytes,
            name="失败全屏截图",
            attachment_type=allure.attachment_type.PNG
        )

# pytest钩子：捕获用例执行结果，用于截图判断
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# ========== 4. 测试结束生成 Allure 环境配置文件 ==========
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """测试结束后生成 Allure 环境配置和执行者信息"""
    allure_dir = "./allure-results"
    os.makedirs(allure_dir, exist_ok=True)
    # ===== environment.properties =====
    env_content = """Browser=Chrome
Browser.Version=auto
OS=Windows 10
Python.Version=3.11.5
Test.Framework=Selenium4 + Pytest
Project=OpenCart_UI_Automation
Base.URL=http://127.0.0.1/opencart
Report.Title=OpenCart Selenium自动化测试报告
"""
    env_path = os.path.join(allure_dir, "environment.properties")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    # ===== executor.json =====
    executor_content = {
        "name": "OpenCart Selenium Automation",
        "type": "local",
        "buildName": "OpenCart Selenium Tests"
    }
    executor_path = os.path.join(allure_dir, "executor.json")
    with open(executor_path, "w", encoding="utf-8") as f:
        json.dump(executor_content, f, indent=2)
    # ===== categories.json =====
    categories_content = [
        {
            "name": "Product defects",
            "matchedStatuses": ["failed"],
            "severity": "critical"
        },
        {
            "name": "Test defects",
            "matchedStatuses": ["broken"],
            "severity": "critical"
        }
    ]
    categories_path = os.path.join(allure_dir, "categories.json")
    with open(categories_path, "w", encoding="utf-8") as f:
        json.dump(categories_content, f, indent=2)
    # ===== allure.properties =====
    props_content = "allure.report.name=OpenCart Selenium自动化测试报告\n"
    props_path = os.path.join(allure_dir, "allure.properties")
    with open(props_path, "w", encoding="utf-8") as f:
        f.write(props_content)
    print("\n✅ Allure 环境配置已生成")

# ========== 5. 测试后解锁账号，清空登录失败记录（MySQL逻辑完全不变） ==========
@pytest.fixture(autouse=True)
def unlock_account_after_test(request):
    """登录用例跑完后，清空登录失败记录，避免账号被锁"""
    yield
    if "login" in str(request.node.fspath).lower():
        try:
            conn = pymysql.connect(
                host="127.0.0.1", port=3306,
                user="root", password="123456",
                database="opencart", charset="utf8mb4"
            )
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE oc_customer_login")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ 清空登录记录失败: {e}")