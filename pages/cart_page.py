from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config import BASE_URL

import logging
logger = logging.getLogger(__name__)

class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input_selector = "input[name='search']"
        self.search_btn_selector = ".btn.btn-light"
        self.add_to_cart_btn_selector = "#button-cart"
        self.checkout_btn_selector = ".btn:has-text('Checkout')"
        self.alert_success = self.page.locator(".alert-success")
        self.cart_empty_text = self.page.locator("#content p:text('Your shopping cart is empty!')")
        self.cart_item = self.page.locator(".table-responsive tbody tr")
        self.product_list = self.page.locator("#product-list")

        self.search_input = self.page.locator(self.search_input_selector)
        self.search_btn = self.page.locator(self.search_btn_selector)

    def navigate(self):
        self.page.goto(f"{BASE_URL}/")
        self.page.wait_for_load_state("networkidle")

    def search_product(self, product_name: str):
        self.search_input.wait_for(state="visible", timeout=10000)
        self.input_text(self.search_input, product_name)
        self.click(self.search_btn)
        self.page.wait_for_load_state("networkidle")
        # 确保有商品列表
        self.page.wait_for_selector("#product-list", timeout=5000)
        if self.page.locator("#product-list .product-thumb").count() == 0:
            raise Exception(f"未找到商品: {product_name}")

    def open_product_detail(self, product_name: str):
        # 使用包含文本，忽略大小写
        locator = self.product_list.locator(f".product-thumb a:has-text('{product_name}')").first
        locator.wait_for(state="visible", timeout=10000)
        self.click(locator)
        self.page.wait_for_load_state("networkidle")

    def add_product_by_ui_click(self):
        add_btn = self.page.locator(self.add_to_cart_btn_selector)
        add_btn.wait_for(state="visible", timeout=10000)
        add_btn.click()
        # 等待成功弹窗
        self.alert_success.wait_for(state="visible", timeout=8000)
        print("✅ 商品加入购物车成功")
        self.page.wait_for_timeout(1000)   # 短暂等待后台写入

    def search_and_add_product(self, product_name: str):
        print(f"开始流程：搜索商品 {product_name}")
        self.search_product(product_name)
        print("搜索完成，打开商品详情页")
        self.open_product_detail(product_name)
        self.add_product_by_ui_click()

    def go_to_checkout(self):
        """进入购物车页面，校验商品存在并点击结算"""
        self.page.goto(f"{BASE_URL}/index.php?route=checkout/cart")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        # 重试最多 3 次（刷新页面）
        for attempt in range(3):
            item_count = self.cart_item.count()
            if item_count > 0:
                break
            self.page.reload()
            self.page.wait_for_timeout(1000)
        else:
            # 最终仍为空，截图并抛出详细错误
            self.page.screenshot(path="cart_empty_debug.png", full_page=True)
            raise Exception("购物车为空，尝试 3 次后仍为空，请检查商品是否成功添加")

        print("✅购物车商品校验通过")
        print("开始寻找Checkout按钮")
        checkout_btn = self.page.locator(self.checkout_btn_selector)
        checkout_btn.wait_for(state="visible", timeout=12000)
        checkout_btn.click()
        print("✅点击Checkout按钮，跳转结算页面")

    def clear_cart(self):
        """清空购物车所有商品，前置调用，防止商品累加"""
        self.page.goto(f"{BASE_URL}index.php?route=checkout/cart")
        delete_btn = self.page.locator("button[name='remove']")
        while delete_btn.count() > 0:
            self.click(delete_btn.first)
            self.wait_network_idle()
        logger.info("购物车已清空")

    # ==================== 新增购物车管理方法 ====================

    def get_cart_total(self):
        """获取购物车商品总价"""
        try:
            total = self.page.locator(".table-responsive .text-right:last-child")
            if total.count() > 0:
                return total.first.text_content().strip()
        except Exception as e:
            logger.warning(f"获取购物车总价失败: {e}")
        return ""

    def get_cart_item_count(self):
        """获取购物车商品行数"""
        try:
            return self.cart_item.count()
        except Exception as e:
            logger.warning(f"获取购物车商品数量失败: {e}")
            return 0

    def update_cart_quantity(self, row_index: int, quantity: int):
        """
        修改购物车指定行的数量
        row_index: 第几行（从1开始）
        quantity: 目标数量
        """
        try:
            quantity_input = self.page.locator(
                f".table-responsive tbody tr:nth-child({row_index}) input[name='quantity']"
            )
            quantity_input.wait_for(state="visible", timeout=5000)
            quantity_input.fill(str(quantity))

            # 点击更新按钮（多种定位方式兜底）
            update_btn = self.page.locator(
                f".table-responsive tbody tr:nth-child({row_index}) button[type='submit']"
            )
            if update_btn.count() == 0:
                update_btn = self.page.locator(
                    f".table-responsive tbody tr:nth-child({row_index}) .btn-primary"
                )
            if update_btn.count() > 0:
                update_btn.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(1000)
                logger.info(f"已更新第{row_index}行商品数量为{quantity}")
            else:
                raise Exception(f"未找到第{row_index}行的更新按钮")
        except Exception as e:
            logger.error(f"更新购物车数量失败: {e}")
            raise

    def remove_cart_item(self, row_index: int):
        """
        删除购物车指定行的商品
        row_index: 第几行（从1开始）
        """
        try:
            # 多种删除按钮定位方式
            remove_btn = self.page.locator(
                f".table-responsive tbody tr:nth-child({row_index}) button[data-bs-target*='remove']"
            )
            if remove_btn.count() == 0:
                remove_btn = self.page.locator(
                    f".table-responsive tbody tr:nth-child({row_index}) .btn-danger"
                )
            if remove_btn.count() == 0:
                remove_btn = self.page.locator(
                    f".table-responsive tbody tr:nth-child({row_index}) button[name='remove']"
                )
            if remove_btn.count() > 0:
                remove_btn.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(1000)
                logger.info(f"已删除第{row_index}行商品")
            else:
                raise Exception(f"未找到第{row_index}行的删除按钮")
        except Exception as e:
            logger.error(f"删除购物车商品失败: {e}")
            raise

    def get_cart_empty_text(self):
        """获取空购物车提示文本"""
        try:
            empty_text = self.page.locator("#content p:has-text('Your shopping cart is empty!')")
            if empty_text.count() > 0:
                return empty_text.first.text_content().strip()
        except Exception as e:
            logger.warning(f"获取空购物车提示失败: {e}")
        return ""

    def get_cart_items_info(self):
        """
        获取购物车所有商品信息
        返回: list of dict, 每个dict包含 name, quantity, price
        """
        items = []
        try:
            rows = self.page.locator(".table-responsive tbody tr").all()
            for row in rows:
                # 获取商品名称
                name = row.locator("td:first-child a").text_content().strip() if row.locator("td:first-child a").count() > 0 else ""
                # 获取数量
                quantity = row.locator("input[name='quantity']").get_attribute("value") if row.locator("input[name='quantity']").count() > 0 else ""
                # 获取价格
                price = row.locator("td:last-child").text_content().strip() if row.locator("td:last-child").count() > 0 else ""
                items.append({
                    "name": name,
                    "quantity": quantity,
                    "price": price
                })
        except Exception as e:
            logger.warning(f"获取购物车商品信息失败: {e}")
        return items