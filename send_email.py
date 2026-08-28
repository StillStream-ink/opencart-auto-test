import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

# ========== 配置区（请修改为您的信息）==========
SMTP_SERVER = "smtp.qq.com"          # 邮件服务器（QQ邮箱用 smtp.qq.com，163用 smtp.163.com）
SMTP_PORT = 465                       # 端口（QQ/163用 465）
SENDER_EMAIL = "your_email@qq.com"   # 发件人邮箱
SENDER_PASSWORD = "your_authorization_code"  # 邮箱授权码（不是登录密码！）
RECEIVER_EMAIL = "receiver@example.com"      # 收件人邮箱
# ===============================================

def send_test_report(test_result, log_content=""):
    """发送测试报告邮件"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = f"OpenCart 测试报告 - {now}"
    if "失败" in test_result:
        subject = f"❌ OpenCart 测试失败！- {now}"
    else:
        subject = f"✅ OpenCart 测试通过 - {now}"
    
    # 邮件正文
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
    # 从命令行参数读取测试结果
    import sys
    if len(sys.argv) > 1:
        test_result = sys.argv[1]
        log_content = sys.argv[2] if len(sys.argv) > 2 else ""
        send_test_report(test_result, log_content)
    else:
        # 默认测试（用于测试邮件功能）
        send_test_report("✅ 测试通过（测试邮件）")