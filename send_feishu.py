import os
import requests
import sys
from datetime import datetime

# ========== 配置区 ==========
WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK", "")
if not WEBHOOK_URL:
    print("⚠️ 未配置 FEISHU_WEBHOOK 环境变量，跳过飞书通知")
# ===========================


def send_markdown_message(title, status, total, passed, failed, skipped, duration):
    """发送 Markdown 格式消息到飞书（interactive 卡片）"""
    if not WEBHOOK_URL:
        return False

    if status == "success":
        status_icon = "✅"
        status_text = "**测试通过**"
        color = "green"
    else:
        status_icon = "❌"
        status_text = "**测试失败**"
        color = "red"

    content = f"""**状态：** {status_text}
**执行时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📊 测试统计**

- 📋 总用例：**{total}**
- ✅ 通过：**{passed}**
- ❌ 失败：**{failed}**
- ⏭️ 跳过：**{skipped}**
- ⏱️ 耗时：**{duration:.1f} 秒**

**📈 通过率：** **{passed/total*100:.1f}%** ({passed}/{total})

> 📎 详细报告请查看 Allure
"""

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": content,
                        "tag": "lark_md"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {
                            "content": "🏷️ 项目: OpenCart UI 自动化测试",
                            "tag": "plain_text"
                        }
                    ]
                }
            ],
            "header": {
                "title": {
                    "content": f"{status_icon} {title}",
                    "tag": "plain_text"
                },
                "template": color
            }
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        result = response.json()

        if result.get("code") == 0:
            print("[OK] 消息已发送到飞书")
            return True
        else:
            print(f"[FAIL] 发送失败：{result}")
            return False
    except Exception as e:
        print(f"[FAIL] 发送异常：{e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) >= 6:
        status = sys.argv[1]
        total = int(sys.argv[2])
        passed = int(sys.argv[3])
        failed = int(sys.argv[4])
        skipped = int(sys.argv[5])
        try:
            duration = float(sys.argv[6]) if len(sys.argv) > 6 else 0
        except ValueError:
            duration = 0

        title = "OpenCart 测试报告"
        send_markdown_message(title, status, total, passed, failed, skipped, duration)
    else:
        # 无参数时发一条测试消息
        msg = sys.argv[1] if len(sys.argv) > 1 else "[OK] 飞书机器人测试成功！"
        data = {
            "msg_type": "text",
            "content": {"text": msg}
        }
        response = requests.post(WEBHOOK_URL, json=data)
        result = response.json()
        if result.get("code") == 0:
            print("[OK] 消息已发送到飞书")
        else:
            print(f"[FAIL] 发送失败：{result}")