#python3  Toolz
#-*- coding: utf-8 -*-
#

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def sendEmail(title,content,receivers,sender='wevie_9@163.com',mail_host="smtp.163.com",mail_user="wevie_9@163.com",mail_pass="Aa123456"):
    '''发送一封普通邮件,文本格式.

    共有七个参数： 包括三个必填参数
    title = 'mail title'        # 邮件标题  必填参数无默认值
    content = 'mail content'    # 邮件内容  必填参数
    receivers = ['Email addr']  # 收件人    必填     列表格式  可多个 列表内用逗号分开
    sender = 'wevie_9@163.com'  # 发件人    最好写全 不然报错 (550, b'Invalid User', 'xiangyu.lin')
    mail_host="smtp.163.com"    # 服务器    用163的
    mail_user="wevie_9@163.com" # 用户名    默认用我的
    mail_pass="Aa123456"        # 授权码    不是密码（网易邮箱可以登录邮箱开启授权码）
    '''

    msg = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    msg['From'] = "{}".format(sender)
    msg['To'] = ",".join(receivers)
    msg['Subject'] = title  #邮件主题

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host,465)  #启用SSL发信, 端口一般是465 qq邮件需要 ssl才能发出去
        #smtplib.SMTP(mail_host,22)
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, msg.as_string())  #发送
        print("mail send success!.")
        #smtpObj.quit() 退出登录
    except smtplib.SMTPException as e: #这种错误类型比较常见
        print(e)
