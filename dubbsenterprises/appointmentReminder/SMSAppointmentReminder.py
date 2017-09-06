'''
Created on Nov 1, 2013

@author: matthassel
'''
from googlevoice import Voice
from googlevoice.util import input

class smsGoogle():
    
    def __init__(self):
        self.username = ''
        self.passwd = ''   
        self.smsNumber = ""
        self.message = "Hello World!" 
        
    def create_sms(self, firstname, appointment_time, company, company_address, company_url):
        sms_text = """{0} appointment reminder:
Where: {1}
When: {2}
        """.format(company,
                   company_address,
                   appointment_time)
        return sms_text   
        
    def main(self):
        voice = Voice()
        voice.login(self.username, self.passwd)
        voice.send_sms(self.smsNumber, self.message)