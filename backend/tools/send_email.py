import smtplib
from email.mime.text import MIMEText
from application.app import logger
from application.configration import app_config


def send(data):
    content = app_config.content
    msg_from = app_config.msg_from
    passwd = app_config.pwd_email
    subject = app_config.subject
    msg_to = data['email']
    url = data['url']
    msg = MIMEText(content % url)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
    except Exception as e:
        logger.error(str(e) + 'when try to send a email to [' + msg_to + ']')
        # print("发送失败")
        return False
    finally:
        s.quit()
    return True
