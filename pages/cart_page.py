from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config import BASE_URL

import logging
logger = logging.getLogger(__name__)

class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # 选择器定义
        self.search_input_selector = "input[name='search']"
        self.search_btn_selector = ".btn.btn-light"
        self.add_to_cart_btn_selector = "#button-cart"
        self.checkout_btn_selector = ".btn:has-text('Checkout')"
        self.alert_success = self.page.locator(".alert-success")
        self.cart_empty_text = self.page.locator("#content p:text('Your shopping cart is empty!')")
        self.cart_item = self.page.locator(".table-responsive tbody tr")
        # 商品列表区域，限定查找范围
        self.product_list = self.page.locator("#product-list")

        # 初始化locator
        self.search_input = self.page.locator(self.search_input_selector)
        self.search_btn = self.page.locator(self.search_btn_selector)

    def navigate(self):
        """访问商城首页"""
        self.page.goto(f"{BASE_URL}/")
        self.page.wait_for_load_state("networkidle")

    def search_product(self, product_name: str):
        """首页搜索商品"""
        self.search_input.wait_for(state="visible", timeout=10000)
        self.input_text(self.search_input, product_name)
        self.click(self.search_btn)
        self.page.wait_for_load_state("networkidle")

    def open_product_detail(self, product_name: str):
        """打开商品详情：限定在商品列表内匹配，避免顶部购物车同名干扰"""
        locator = self.product_list.get_by_text(product_name, exact=True).first
        locator.wait_for(state="visible", timeout=10000)
        self.click(locator)
        self.page.wait_for_load_state("networkidle")

    def add_product_by_ui_click(self):
        """原生点击加入购物车，复刻人工操作"""
        print("点击页面原生【Add To Cart】按钮")
        add_btn = self.page.locator(self.add_to_cart_btn_selector)
        add_btn.wait_for(state="visible", timeout=10000)
        add_btn.click()

        # 等待成功弹窗
        self.alert_success.wait_for(state="visible", timeout=8000)
        print("✅成功弹窗出现")
        # 等待后台写入session
        self.page.wait_for_timeout(3000)

    def search_and_add_product(self, product_name: str):
        """搜索→打开详情→原生按钮加购"""
        print(f"开始流程：搜索商品 {product_name}")
        self.search_product(product_name)
        print("搜索完成，打开商品详情页")
        self.open_product_detail(product_name)
        self.add_product_by_ui_click()

    def go_to_checkout(self):
        """进入购物车页面，校验商品存在并点击结算"""
        print("进入购物车页面")
        self.page.goto(f"{BASE_URL}/index.php?route=checkout/cart")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.page.screenshot(path="cart_page_debug.png", full_page=True)

        # 调试：打印购物车商品数量
        item_count = self.cart_item.count()
        print(f"【调试】购物车商品行数：{item_count}")

        # 双重校验：有商品行就认为加购成功
        if item_count == 0:
            if self.cart_empty_text.is_visible(timeout=1000):
                raise Exception("购物车为空！商品未成功加入会员购物车！")

        print("✅购物车商品校验通过")
        print("开始寻找Checkout按钮")
        checkout_btn = self.page.locator(self.checkout_btn_selector)
        checkout_btn.wait_for(state="visible", timeout=12000)
        checkout_btn.click()
        print("✅点击Checkout按钮，跳转结算页面")

    def clear_cart(self):
        """清空购物车所有商品，前置调用，防止商品累加"""
        self.page.goto(f"{BASE_URL}index.php?route=checkout/cart")
        # 循环删除所有商品
        delete_btn = self.page.locator("button[name='remove']")
        while delete_btn.count() > 0:
            self.click(delete_btn.first)
            self.wait_network_idle()
        logger.info("购物车已清空")