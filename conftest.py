import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from config import TEST_EMAIL, TEST_PASSWORD


@pytest.fixture(scope="function")
def driver():
    # Edge配置
    edge_options = Options()
    edge_options.add_argument("--window-size=1920,1080")
    # edge_options.add_argument("--headless=new") # 无头模式，需要时打开注释
    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=edge_options
    )
    driver.implicitly_wait(5)
    yield driver
    # 用例结束关闭浏览器
    driver.quit()


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """登录夹具，登录成功"""
    login_page = LoginPage(driver)
    login_page.navigate()
    login_page.login(TEST_EMAIL, TEST_PASSWORD)
    return driver


@pytest.fixture(scope="function")
def cart_clean(logged_in_driver):
    """
    核心：用例执行前后，保证购物车是空的
    前置：登录后清空购物车
    yield：把driver传给测试用例
    后置：再次清空购物车，防止数据残留
    """
    cart_page = CartPage(logged_in_driver)
    cart_page.open_cart()
    # 前置清理：循环删除全部商品
    try:
        items = cart_page.get_cart_items_info()
        while len(items) > 0:
            cart_page.remove_item()
            items = cart_page.get_cart_items_info()
    except Exception:
        pass

    yield logged_in_driver

    # 后置清理：再次清空购物车
    try:
        cart_page.open_cart()
        items = cart_page.get_cart_items_info()
        while len(items) > 0:
            cart_page.remove_item()
            items = cart_page.get_cart_items_info()
    except Exception:
        pass