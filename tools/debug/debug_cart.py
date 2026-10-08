from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from config import TEST_EMAIL, TEST_PASSWORD

options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless=new") # 需要无头就打开注释

driver = webdriver.Edge(
    service=Service(EdgeChromiumDriverManager().install()),
    options=options
)

try:
    login = LoginPage(driver)
    login.navigate()
    login.login(TEST_EMAIL, TEST_PASSWORD)

    # 直接访问购物车页面
    driver.get("http://127.0.0.1/opencart/index.php?route=checkout/cart")

    # 等待页面AJAX渲染完毕，给足够时间加载购物车表格
    import time
    time.sleep(4)

    # 获取购物车表格内部完整HTML
    table_elem = driver.find_element(By.CSS_SELECTOR, ".table-responsive")
    inner_html = table_elem.get_attribute("innerHTML")

    print("\n==================== 购物车表格HTML源码开始 ====================\n")
    print(inner_html)
    print("\n==================== 购物车表格HTML源码结束 ====================\n")

finally:
    input("\n>>> 按回车键关闭浏览器...")
    driver.quit()