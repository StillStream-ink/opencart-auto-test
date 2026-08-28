# config.py
import os

# 从环境变量读取，如果没有则使用默认值
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1/opencart")
TEST_EMAIL = os.getenv("TEST_EMAIL", "mytest203@test.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Open2026")
WAIT_TIMEOUT = 15000

# BASE_URL = "http://127.0.0.1/opencart"   # 统一为127.0.0.1
# TEST_EMAIL = "mytest203@test.com"        # 成功项目验证过的账号
# TEST_PASSWORD = "Open2026"               # 对应的密码
# WAIT_TIMEOUT = 15000