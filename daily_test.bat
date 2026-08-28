@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    OpenCart UI 自动化测试（定时任务）
echo ========================================

cd /d "%~dp0"
echo [OK] 当前目录：%cd%

echo.
echo [INFO] 检查 XAMPP...
tasklist /FI "IMAGENAME eq httpd.exe" 2>nul | find /I "httpd.exe" >nul
if %errorlevel% neq 0 (
    echo [WARN] XAMPP 未运行，正在启动...
    start "" "C:\xampp\xampp-control.exe"
    echo [INFO] 等待 XAMPP 启动（15秒）...
    timeout /t 15 /nobreak >nul
) else (
    echo [OK] XAMPP 已在运行
)

echo.
echo [INFO] 开始运行测试...
set start_time=%time%

py -m pytest tests/ -v --alluredir=./allure-results --clean-alluredir
set test_result=%errorlevel%

set end_time=%time%

echo.
echo [INFO] 计算耗时...
for /f %%i in ('powershell -command "& { $diff = (Get-Date -Date '%end_time%') - (Get-Date -Date '%start_time%'); [math]::Round($diff.TotalSeconds) }"') do set duration=%%i
if "%duration%"=="" set duration=0

echo [INFO] 耗时：%duration% 秒

echo.
echo [INFO] 生成 Allure 报告...
if exist ".\allure-history" (
    allure generate ./allure-results -o ./allure-report --clean --history ./allure-history
) else (
    allure generate ./allure-results -o ./allure-report --clean
)

echo.
echo [INFO] 保存历史数据...
set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
if not exist ".\allure-history" mkdir allure-history
xcopy /E /I .\allure-results .\allure-history\run_%timestamp% >nul

echo.
echo [INFO] 修改报告标题...
powershell -Command "$file = 'allure-report/index.html'; $content = Get-Content $file -Raw -Encoding UTF8; $newContent = $content -replace '<title>Allure Report</title>', '<title>OpenCart 自动化测试报告</title>'; $newContent | Out-File $file -Encoding UTF8"

echo.
if %test_result% neq 0 (
    echo [FAIL] 测试失败，错误码：%test_result%
    set "result_msg=[FAIL] 测试失败，错误码：%test_result%"
    py send_feishu.py "failed" 14 13 1 0 %duration%
) else (
    echo [OK] 测试全部通过！
    set "result_msg=[OK] 测试通过，共14个用例"
    py send_feishu.py "success" 14 14 0 0 %duration%
)

echo.
echo ========================================
echo [OK] 测试完成！
echo ========================================

REM 记录日志
for /f "tokens=1-3 delims=/- " %%a in ('date /t') do set log_date=%%a-%%b-%%c
for /f "tokens=1-2 delims=:. " %%a in ('time /t') do set log_time=%%a:%%b
echo %log_date% %log_time% - %result_msg% 耗时：%duration%秒 >> test_log.txt

pause