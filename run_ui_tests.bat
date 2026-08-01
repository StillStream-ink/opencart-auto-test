@echo off
set PROJECT_DIR=E:\OpenCart测试项目_20260717\opencart_auto_test

cd /d "%PROJECT_DIR%"

echo ===== 1. 运行测试 =====
pytest tests/test_checkout_ui.py -v --headed --alluredir=./allure-results --clean-alluredir

echo ===== 2. 恢复配置文件 =====
copy "%PROJECT_DIR%\environment.properties" "%PROJECT_DIR%\allure-results\"
copy "%PROJECT_DIR%\executor.json" "%PROJECT_DIR%\allure-results\"

echo ===== 3. 生成报告 =====
allure serve ./allure-results

pause