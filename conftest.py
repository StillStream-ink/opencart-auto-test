import pytest
import allure
import os
import json
import logging

from pages.login_page import LoginPage
from config import TEST_EMAIL, TEST_PASSWORD

# 创建日志目录
os.makedirs("logs", exist_ok=True)

# 配置日志：同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/test_run.log", encoding="utf-8")
    ],
    force=True   
)

# ========== 1. 浏览器视口配置 ==========
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "no_viewport": False,
    }


# ========== 2. 固定浏览器视口大小 ==========
@pytest.fixture(autouse=True)
def set_browser_window(page):
    """固定浏览器视口大小，并尝试移动到屏幕左上角"""
    page.set_viewport_size({"width": 1600, "height": 900})
    try:
        page.evaluate("window.moveTo(0, 0)")
    except Exception:
        pass  # 无头模式忽略
    yield


# ========== 3. 已登录的 page Fixture ==========
@pytest.fixture
def logged_in_page(page):
    """返回已完成登录的 page 对象，供购物车、结算等用例复用"""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(TEST_EMAIL, TEST_PASSWORD)
    login_page.verify_login_success()
    return page


# ========== 4. 失败自动截图 ==========
@pytest.fixture(autouse=True)
def capture_screenshot(request, page):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_bytes = page.screenshot(full_page=True)
        allure.attach(
            screenshot_bytes,
            name="失败全屏截图",
            attachment_type=allure.attachment_type.PNG
        )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# ========== 5. 测试结束后生成 Allure 配置文件 ==========
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """测试结束后生成 Allure 环境配置和执行者信息"""
    allure_dir = "./allure-results"
    os.makedirs(allure_dir, exist_ok=True)

    # ===== 5.1 environment.properties =====
    env_content = """Browser=Microsoft Edge
Browser.Version=127
OS=Windows 10
Python.Version=3.11.5
Test.Framework=Playwright + Pytest
Project=OpenCart_UI_Automation
Base.URL=http://127.0.0.1/opencart
Report.Title=OpenCart 自动化测试报告
"""
    env_path = os.path.join(allure_dir, "environment.properties")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    # ===== 5.2 executor.json =====
    executor_content = {
        "name": "OpenCart UI Automation",
        "type": "local",
        "buildName": "OpenCart Playwright Tests"
    }
    executor_path = os.path.join(allure_dir, "executor.json")
    with open(executor_path, "w", encoding="utf-8") as f:
        json.dump(executor_content, f, indent=2)

    # ===== 5.3 categories.json =====
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

    # ===== 5.4 allure.properties（报告标题） =====
    props_content = "allure.report.name=OpenCart 自动化测试报告\n"
    props_path = os.path.join(allure_dir, "allure.properties")
    with open(props_path, "w", encoding="utf-8") as f:
        f.write(props_content)

    print("\n✅ Allure 环境配置已生成")