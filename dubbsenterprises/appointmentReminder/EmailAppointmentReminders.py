'''
Created on Oct 15, 2013

@author: matthassel
'''
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailAppointmentReminders():
    
    def __init__(self):
        self.SMTP_SERVER = "localhost"
        self.SMTP_PORT = 25
        self.EMAIL_FROM = "test@dubbsenterprises.com"
        self.email_to = "matthew.hassel@gmail.com"
        self.email_subject = "REMINDER:"
    
    def email_create_message(self, firstname, appointment_time, company, company_address, company_url):
        email_text = """
        Hello, {0}!
Just wanted to send a friendly appointment
reminder for your appointment at {1}:
Where: {2}
When: {3}
        
Company URL: {4}
        """.format(firstname,
                   company,
                   company_address,
                   appointment_time,
                   company_url)
        email_html="""
        <html>
          <head></head>
          <body>
          <h3>Appointment Reminder</h3>
          <p>Hi, {0}!</p>
          <p>Just wanted to send a friendly appointment reminder for
          your appointment at {1}:<br><br>
          <b>Where:</b> {2}<br>
          <b>Time:</b> {3}<br><br>
          <b>Company URL:</b> <a href="http://{4}">{4}</a>
          </p>
          </body>
        </html>
        """.format(firstname,
                   company,
                   company_address,
                   appointment_time,
                   company_url)
        return email_text, email_html
    
    def email_send_email(self, email_text, email_html,debuglevel=False):
        pass
        self.msg = MIMEMultipart('alternative')
        self.part1 = MIMEText(email_text, 'plain')
        self.part2 = MIMEText(email_html, 'html')
        #self.msg = MIMEText(email_text)
        self.msg['Subject'] = self.email_subject
        self.msg['From'] = self.EMAIL_FROM
        self.msg['To'] = self.email_to
        self.msg.attach(self.part1)
        self.msg.attach(self.part2)
        self.mail = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        self.mail.set_debuglevel(debuglevel)
        self.mail.sendmail(self.EMAIL_FROM, self.email_to, self.msg.as_string())
        self.mail.quit()