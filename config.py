import os
from urllib.parse import urlparse
# —— 环境 ——
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1/opencart")
BASE_DOMAIN = urlparse(BASE_URL).hostname or "127.0.0.1"  # ✅ 新增：从 URL 解析，禁止硬编码
# —— 账号 ——
TEST_EMAIL = os.getenv("TEST_EMAIL", "mytest203@test.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Open2026")
# —— 超时 ——
WAIT_TIMEOUT = 15

# —— MySQL数据库配置（环境变量优先，本地默认值）——
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PWD = os.getenv("DB_PWD", "123456")
DB_NAME = os.getenv("DB_NAME", "opencart")