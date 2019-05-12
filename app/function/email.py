import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class Email:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email
        self.ip_frontend = os.environ.get('IP_FRONTEND')

    def send_reset_password_email(self):
        sender = "Intelligist platfrom <chana.su@intelligist.co.th>"
        receivers = self.email
        subject = "Intelligist Plaform : Reset Password."
        link = "{}/resetpassword/{}".format(self.ip_frontend, self.user_id)
        footer ="<br><br><br>Team Intelligist Platform" + "<br>Call Center: +66 2 257 7000" + "<br>Email: chana.su@intelligist.co.th"
        body_text = "Thanks for coming on Intelligist Platform. Do you forgot password? \n Click below to reset your password \nTeam Intelligist Platform \nCall Center: +66 2 257 7000 \r Email: chana.su@intelligist.co.th"
        body_html = "<p style='text-indent:40px;padding-left:40px;padding-right:40px;font-size: 14px;width: 410px; margin-right: auto; margin-left: auto;'>Thanks for coming on Intelligist Platform. Do you forgot password?<br>Click below to reset your password</p> <a href='" + str(link) + "' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Reset Password</a>" + footer

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = receivers
        text = MIMEText(body_text, "plain")
        html = MIMEText(body_html, "html")
        
        message.attach(text)
        message.attach(html)

        try:
            server = smtplib.SMTP(os.environ.get('MAIL_SERVER'))
            server.sendmail(sender, receivers, message.as_string())
            return True
        except Exception as e:
            return False        
    
    def send_confirm_email(self):
        sender = "Intelligist platfrom <chana.su@intelligist.co.th>"
        receivers = self.email
        subject = "Intelligist Plaform : Please Comfirm your Email for activate your account."
        link = "{}/confirm/{}".format(self.ip_frontend, self.user_id)
        footer ="<br><br><br>Team Intelligist Platform" + "<br>Call Center: +66 2 257 7000" + "<br>Email: chana.su@intelligist.co.th"
        body_text = "Thanks for registering for an account on Intelligist Platform\n Before we get started, we just need to confirm that this is you.\n Click below to verify your email address Verify Email \nTeam Intelligist Platform \nCall Center: +66 2 257 7000 \r Email: chana.su@intelligist.co.th"
        body_html = "<p style='text-indent:40px;padding-left:40px;padding-right:40px;font-size: 14px;width: 410px; margin-right: auto; margin-left: auto;'>Thanks for registering for an account on Intelligist Platform<br> Before we get started, we just need to confirm that this is you.<br>Click below to verify your email address</p> <a href='" + str(link) + "' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Verify Email</a>" + footer

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = receivers
        text = MIMEText(body_text, "plain")
        html = MIMEText(body_html, "html")
        
        message.attach(text)
        message.attach(html)

        try:
            server = smtplib.SMTP(os.environ.get('MAIL_SERVER'))
            server.sendmail(sender, receivers, message.as_string())
            return True
        except Exception as e:
            return False

