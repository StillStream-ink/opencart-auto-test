@echo off
chcp 65001 >nul
set PROJECT_DIR=E:\OpenCart测试项目_20260717\opencart-auto-test

cd /d "%PROJECT_DIR%"

echo ========================================
echo   OpenCart UI 自动化测试
echo ========================================

echo.
echo [1/4] 运行所有测试...
py -m pytest tests/ -v --alluredir=./allure-results --clean-alluredir

echo.
echo [2/4] 生成 Allure 报告（含历史趋势）...
if exist ".\allure-history" (
    allure generate ./allure-results -o ./allure-report --clean --history ./allure-history
) else (
    allure generate ./allure-results -o ./allure-report --clean
)

echo.
echo [3/4] 保存本次数据到历史...
set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
if not exist ".\allure-history" mkdir allure-history
xcopy /E /I .\allure-results .\allure-history\run_%timestamp% >nul

echo.
echo [4/4] 修改报告标题...
powershell -Command "$file = 'allure-report/index.html'; $content = Get-Content $file -Raw -Encoding UTF8; $newContent = $content -replace '<title>Allure Report</title>', '<title>OpenCart 自动化测试报告</title>'; $newContent | Out-File $file -Encoding UTF8"

echo.
echo ✅ 测试完成！
echo 📊 报告路径：%PROJECT_DIR%\allure-report\index.html

echo.
echo ===== 打开报告 =====
start "" "./allure-report/index.html"

pause