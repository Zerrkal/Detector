import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AlertNotificationEmail:

    def __init__(self, capture_index):
        self.password = ""
        self.from_email = "zerrkal@gmail.com"  # must match the email used to generate the password
        self.to_email = "zerkal_rr@ffeks.dnu.edu.ua"  # receiver email

        self.server = smtplib.SMTP('smtp.gmail.com: 587')
        self.server.starttls()
        self.server.login(self.from_email, self.password)

    def send(self, object_detected=1):
        message = MIMEMultipart()
        message['From'] = self.from_email
        message['To'] = self.to_email
        message['Subject'] = "Security Alert"
        # Add in the message body
        message_body = f'ALERT - {object_detected} objects has been detected!!'

        message.attach(MIMEText(message_body, 'plain'))
        self.server.sendmail(self.from_email, self.to_email, message.as_string())

    def chack(self):
        return True
    
    def quit_server(self):
        self.server.quit()