import os


class AppConfig(object):
    root_path = str(os.path.dirname(__file__))[:-len('application')]
    origins = 'origins'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://webapp:@127.0.0.1:3306/webapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    host = '127.0.0.1'
    port = 6379
    db_code = 1
    pwd = ''
    log_path = 'log/error.log'
    msg_from = '11111111@qq.com'
    pwd_email = ''
    subject = "欢迎注册"
    content = "离注册成功就差一步了！\n" \
              "点击 %s 对邮箱进行认证"
    base_host = 'http://127.0.0.1/fmt/#/verify?code='


app_config = AppConfig()
