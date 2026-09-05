@echo off
chcp 65001 >nul
set PROJECT_DIR=E:\OpenCart测试项目_20260717\opencart-auto-test

cd /d "%PROJECT_DIR%"

echo ========================================
echo   OpenCart UI 自动化测试
echo ========================================

echo.
echo [1/4] 运行测试（不清空历史数据，用于趋势图累积）...
REM 去掉 --clean-alluredir，让多次运行的数据累积
py -m pytest tests/ -v --alluredir=./allure-results

echo.
echo [2/4] 生成 Allure 报告（不带 --history，Allure 会自动扫描所有历史数据）...
allure generate ./allure-results -o ./allure-report --clean

echo.
echo [3/4] 修改报告标题...
powershell -Command "$file = 'allure-report/index.html'; $content = Get-Content $file -Raw -Encoding UTF8; $newContent = $content -replace '<title>Allure Report</title>', '<title>OpenCart 自动化测试报告</title>'; $newContent | Out-File $file -Encoding UTF8"

echo.
echo ✅ 测试完成！
echo 📊 报告路径：%PROJECT_DIR%\allure-report\index.html

echo.
echo ===== 打开报告 =====
allure open ./allure-report
pause