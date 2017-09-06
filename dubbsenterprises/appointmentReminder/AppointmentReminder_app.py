#!/usr/bin/python
'''
Created on Oct 21, 2013

@author: matthassel

@summary: Sends a reminder text (google voice) and reminder email 2 hours before a customer's
appointment.
'''
import MySQLdb
import MySQLdb.cursors
import datetime
from time import sleep
import EmailAppointmentReminders
import SMSAppointmentReminder
import sys, traceback

class Appointment_DB():
    
    def __init__(self):
        self.appointments = [] # appointments table
        self.host = 'opchweb0004.matthassel.com'
        self.user = 'dubbsenterprises'
        self.passwd = 'W3bW3bW3b'
        self.database = 'dubbsenterprises'
        
    def db_connect(self, dict=True):
        """Connect to database and return db object."""
        
        if dict == True:
            cc = MySQLdb.cursors.DictCursor
        else:
            cc = MySQLdb.cursors.Cursor
        self.db = MySQLdb.connect(host=self.host,
                     user=self.user,
                     passwd=self.passwd,
                     db=self.database,
                     cursorclass=cc)
        return self.db
    
    def db_execute_query(self, db, sql, results=True):
        """Execute query and return results list object."""
        
        result_list = []
        cursor = db.cursor()
        cursor.execute(sql)
        if results == True:
            for row in cursor.fetchall():
                result_list.append(row)
            cursor.close()
            return result_list

    def appointment_db_query(self):
        """queries the appointments table and returns a dictionary of appointments"""
        
        appointments = []
        sql = """
        SELECT appt.id AS appt_id, appt.customer_id AS cust_id,
        DATE_FORMAT(appt.startDate, '%W %m/%d/%Y %l:%i %p') AS appt_lt,
        CONVERT_TZ(DATE_SUB(appt.startDate, INTERVAL 2 HOUR), pref.value, 'UTC') AS reminder_utc,
        comp.id AS comp_id, comp.name AS comp_name, comp.domain AS comp_domain, pref.value AS comp_timezone,
        (SELECT value from preferences AS p WHERE name='receipt header' AND p.company_id=comp.id) AS comp_address,
        cust.email AS cust_email, cust.firstname AS cust_fname, cust.surname AS cust_lname, cust.phone_num as cust_phone
        FROM appointments AS appt
        INNER JOIN companies as comp ON comp.id=appt.company_id
        INNER JOIN customers as cust ON cust.id=appt.customer_id
        INNER JOIN preferences AS pref ON pref.company_id=comp.id
        WHERE (DATE(appt.startDate)=DATE(CONVERT_TZ(CURDATE(), 'UTC', pref.value)) 
        OR DATE(appt.startDate)=DATE(CONVERT_TZ(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'UTC', pref.value)))
        AND pref.name='timezone';
        """
        db = self.db_connect()
        appointments_db_query = self.db_execute_query(db, sql)
        appointments = appointments_db_query
        return appointments
    
    def reminder_db_query(self):
        """queries the appointments_reminder table for all reminders where the date is
        the current date or the current date + 1"""
        
        reminder_results = []
        sql = """
        SELECT
        appt_reminders_appt_id,
        appt_reminders_reminder_type_id,
        appt_reminders_reminder_time
        FROM appointments_reminders 
        WHERE DATE(appt_reminders_reminder_time)=CURDATE()
        OR DATE(appt_reminders_reminder_time)=DATE(DATE_ADD(CURDATE(), INTERVAL 1 DAY))
        OR DATE(appt_reminders_reminder_time)=DATE(DATE_SUB(CURDATE(), INTERVAL 1 DAY));
        """
        db = self.db_connect(dict=False)
        reminder_query = self.db_execute_query(db, sql)
        for row in reminder_query:
            reminder_results.append((row[0],row[1]))
        return reminder_results
    
    def reminder_db_insert(self, appt_id, appt_cust_id, appt_type_id, appt_reminder_time, appt_comp_timezone):
        """Inserts records into the reminders table to later be used for validating
        whether an appointment reminder has been sent or not"""
        
        sql = """
        INSERT INTO appointments_reminders
        (appt_reminders_appt_id,
        appt_reminders_appt_customer_id,
        appt_reminders_reminder_type_id,
        appt_reminders_reminder_time)
        VALUE ('{0}','{1}','{2}', CONVERT_TZ('{3}', '{4}', 'UTC'));
        """.format(appt_id, appt_cust_id, appt_type_id, appt_reminder_time, appt_comp_timezone)
        db = self.db_connect()
        self.db_execute_query(db, sql)
        
    def server_time_now(self):
        """returns the server time as utc time"""
        return datetime.datetime.now().utcnow()
    
    def run(self):
        """the main application"""
        while True:
            # Create instance of appointment app, email app, and sms app.
            appt_app = Appointment_DB()
            email_app = EmailAppointmentReminders.EmailAppointmentReminders()
            sms_app = SMSAppointmentReminder.smsGoogle()
            
            # Get server's current time
            current_time = appt_app.server_time_now()
            
            # get appointments from db query
            appointments = appt_app.appointment_db_query()
            
            # get remindres from db query
            reminders = appt_app.reminder_db_query()
            
            # Loop through appointments
            for a in appointments:
                # variables used for reminder_insert_query
                appt_id = a['appt_id']
                appt_cust_id = a['cust_id']
                appt_email_type_id = 1
                appt_sms_type_id = 2
                appt_reminder_time = a['reminder_utc']
                
                
                # EMAIL setup    
                appt_cust_firstname = a['cust_fname'] 
                appt_cust_email = a['cust_email']
                appt_appt_time = a['appt_lt']   
                appt_comp_name = a['comp_name']     
                appt_comp_address = a['comp_address']
                appt_comp_url = a['comp_domain']
                appt_comp_timezone = a['comp_timezone']
                
                # SMS setup
                appt_cust_phone = a['cust_phone']
                
                
                # Send Email and Insert Reminders db accordingly
                if appt_reminder_time < current_time and (appt_id, appt_email_type_id) not in reminders:
                    #print "email"
                    #print "appointment_id: ", appt_id                

                                     
                    # EMAIL
                    msg_body, msg_html = email_app.email_create_message(appt_cust_firstname, appt_appt_time, appt_comp_name, appt_comp_address, appt_comp_url)
                    email_app.email_to = appt_cust_email
                    email_app.email_subject = "REMINDER: {0} - {1}".format(appt_comp_name, appt_appt_time)
                    email_app.email_send_email(msg_body, msg_html, debuglevel=False)
                    
                    # reminder table update after email is sent
                    app.reminder_db_insert(appt_id, appt_cust_id, appt_email_type_id , appt_reminder_time, appt_comp_timezone)
                    
                # Send SMS and Insert Reminders db accordingly
                if appt_reminder_time < current_time and (appt_id, appt_sms_type_id) not in reminders:
                    #print "sms"
                    #print "appointment_id: ", appt_id
                    
                    # SMS
                    sms_app.message = sms_app.create_sms(appt_cust_firstname, appt_appt_time, appt_comp_name, appt_comp_address, appt_comp_url)
                    sms_app.smsNumber = appt_cust_phone
                    try:
                        sms_app.username = 'username'
                        sms_app.passwd = 'password'
                        sms_app.main()
                    except:
                        print "Exception in user code (SMS LIMIT most likely has been reached)"
                        print '-'*60
                        traceback.print_exc(file=sys.stdout)
                        print '-'*60
                        pass
                                            
                    # reminder table update after sms is sent
                    app.reminder_db_insert(appt_id, appt_cust_id, appt_sms_type_id, appt_reminder_time, appt_comp_timezone)
            sleep(10)
if __name__ == '__main__':
    saveout = sys.stdout
    fsock = open('appointmentReminderError.log', 'w')
    sys.stdout = fsock
    app = Appointment_DB()
    app.run()
    sys.stdout = saveout
    fsock.close()