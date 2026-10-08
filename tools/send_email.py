import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

# ========== 配置区（从环境变量读取）==========
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")
# ===========================================


def send_test_report(test_result, log_content=""):
    """发送测试报告邮件"""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
        print("⚠️ 未配置 SENDER_EMAIL / SENDER_PASSWORD / RECEIVER_EMAIL 环境变量，跳过邮件发送")
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "失败" in test_result:
        subject = f"❌ OpenCart 测试失败！- {now}"
    else:
        subject = f"✅ OpenCart 测试通过 - {now}"

    body = f"""
    ========================================
       OpenCart UI 自动化测试报告
    ========================================

    执行时间：{now}
    测试结果：{test_result}

    ========================================
    详细日志：
    {log_content}
    ========================================
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()

        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        print("📧 邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_result = sys.argv[1]
        log_content = sys.argv[2] if len(sys.argv) > 2 else ""
        send_test_report(test_result, log_content)
    else:
        send_test_report("✅ 测试通过（测试邮件）")