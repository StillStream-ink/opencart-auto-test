import pytest
import allure
import os
import json


# ========== 1. 浏览器视口配置 ==========
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        # ✅ 设置窗口位置（左上角）
        "no_viewport": False,
    }

# ✅ 添加一个 fixture 设置窗口位置
@pytest.fixture(autouse=True)
def set_window_position(page):
    """设置浏览器窗口位置为屏幕左上角"""
    page.set_viewport_size({"width": 1600, "height": 900})
    # 用 JavaScript 移动窗口（Playwright 原生不支持移动窗口，但可以用 page.evaluate）
    page.evaluate("window.moveTo(0, 0)")
    yield

# ========== 2. 失败自动截图 ==========
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


# ========== 3. 设置 Allure 报告标题 ==========
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """设置 Allure 报告标题"""
    # 通过环境变量设置标题
    os.environ["ALLURE_REPORT_NAME"] = "OpenCart 自动化测试报告"


# ========== 4. 测试结束后生成 Allure 配置文件 ==========
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """测试结束后生成 Allure 环境配置和执行者信息"""
    allure_dir = "./allure-results"
    os.makedirs(allure_dir, exist_ok=True)

    # ===== 4.1 environment.properties =====
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

    # ===== 4.2 executor.json =====
    executor_content = {
        "name": "OpenCart UI Automation",
        "type": "local",
        "buildName": "OpenCart Playwright Tests"
    }
    executor_path = os.path.join(allure_dir, "executor.json")
    with open(executor_path, "w", encoding="utf-8") as f:
        json.dump(executor_content, f, indent=2)

    # ===== 4.3 categories.json（自定义缺陷分类，可选） =====
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

    print("\n✅ Allure 环境配置已生成")

@pytest.fixture(autouse=True)
def set_browser_window(page):
    """固定浏览器视口大小，并居中窗口"""
    # 设置视口大小（视口 = 浏览器内部区域）
    page.set_viewport_size({"width": 1600, "height": 900})
    # 尝试将浏览器窗口移到屏幕左上角（部分浏览器允许）
    try:
        page.evaluate("window.moveTo(0, 0)")
    except:
        pass  # 无头模式忽略
    yield