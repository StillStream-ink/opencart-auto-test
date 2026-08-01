import pytest
import allure
import os
import json

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080}
    }

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


# ===== 新增：测试结束后生成 Allure 配置文件 =====
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """测试结束后生成 Allure 环境配置和执行者信息"""
    allure_dir = "./allure-results"
    os.makedirs(allure_dir, exist_ok=True)

    # environment.properties
    env_content = """Browser=Microsoft Edge
Browser.Version=127
OS=Windows 10
Python.Version=3.11.5
Test.Framework=Playwright + Pytest
Project=OpenCart_UI_Automation
Base.URL=http://localhost/opencart
"""
    env_path = os.path.join(allure_dir, "environment.properties")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    # executor.json
    executor_content = {
        "name": "OpenCart UI Automation",
        "type": "local",
        "reportUrl": "https://github.com/你的用户名/opencart-auto-test",
        "buildName": "OpenCart Playwright Tests"
    }
    executor_path = os.path.join(allure_dir, "executor.json")
    with open(executor_path, "w", encoding="utf-8") as f:
        json.dump(executor_content, f, indent=2)