from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
import time
import json

options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

driver.get("http://127.0.0.1/opencart/index.php?route=account/login")
time.sleep(2)

# 填入账号密码
driver.find_element(By.ID,"input-email").send_keys("mytest203@test.com")
driver.find_element(By.ID,"input-password").send_keys("Open2026")
time.sleep(2)

# 提交表单，拿到后端返回的json
form = driver.find_element(By.CSS_SELECTOR,"#form-login")
# 获取跳转链接
redirect_url = driver.execute_script("""
    let form = arguments[0];
    let fd = new FormData(form);
    return await fetch(form.action, {method:'POST', body:fd}).then(res=>res.json()).then(data=>data.redirect);
""", form)

# 手动跳转登录后的账户页面
driver.get(redirect_url)

time.sleep(3)
print("✅登录成功，当前页面url:", driver.current_url)
input("回车关闭浏览器")
driver.quit()