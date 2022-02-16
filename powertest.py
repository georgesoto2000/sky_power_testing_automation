import os, os.path, smtplib, ssl
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sky

#PROCESS FUNCTIONS

def end_of_test_time(d): #Length of the test, in days, is taken as an argument and the date of the end of the test is returned, all tests finish at 7am 
    t1=datetime.now()
    t2=(datetime.now()+timedelta(days=d))
    t2=t2.replace(hour=7, minute=0, second=0, microsecond=0)
    return t2

def logger(end_time,test,powerbricks): #logs power for all platforms at the same time creating a different csv file for each
    print("logging power...")
    while((datetime.now()<end_time)): #loop executed until the end of time/date
        for brick in powerbricks:
            filename=brick.platform+"_"+test
            f = open(filename,'a')
            f.write(brick.get_power())
            f.flush()
            f.close()


def send_email(name,powerbricks): #sends emails for each platform with test results 
    n=0
    print("sending email...")
    for brick in powerbricks:
        filename=str(brick.platform+"_"+name)
        subject = "Test results"
        body = "Results attached as CSV file" #message returned if the test has been conducted successfully
        sender_email = "automatedtests.sky@gmail.com"
        receiver_email = "george.soto@sky.uk"
        password = "Tester1234"
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject 
        message.attach(MIMEText(body, "plain")) # Add body to email
        with open(filename, "rb") as attachment: # Open file in binary mode
                part = MIMEBase("application", "octet-stream")# Add file as application/octet-stream
                part.set_payload(attachment.read())# Email client can usually download this automatically as attachment   
        encoders.encode_base64(part)# Encode file in ASCII characters to send by email 
        part.add_header( # Add header as key/value pair to attachment part
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        message.attach(part)  # Add attachment to message and convert message to string
        text = message.as_string()
        context = ssl.create_default_context() # Log in to server using secure context and send email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)
            print("email sent")
            os.remove(filename)
        except:
            print("couldn't send email ", brick.platform)
        n=n+1


#TESTS
        
def DAILY_REBOOT_ACTIVE(STBs, powerbricks):
    for STB in STBs:
        STB.set_active()
        STB.press("power")
    name="DAILY_REBOOT_ACTIVE.csv"
    logger(end_of_test_time(3),name,powerbricks)
    send_email(name,powerbricks)

def DAILY_REBOOT_NONE(STBs, powerbricks):
    for STB in STBs:
        STB.set_none() 
        STB.press("power")
    name="DAILY_REBOOT_NONE.csv"
    logger(end_of_test_time(3),name,powerbricks)
    send_email(name,powerbricks)

def DAILY_REBOOT_ECO_NONE(STBs, powerbricks):
    for STB in STBs:
        STB.set_eco()
        STB.press()
    name="DAILY_REBOOT_ECO_NONE.csv"
    logger(end_of_test_time(1),name)
    for STB in STBs:
        STB.set_none()
        STB.press("power")
    logger(end_of_test_time(2),name,powerbricks)
    send_email(name,powerbricks)

def DAILY_REBOOT_ECO_ACTIVE(STBs, powerbricks):
    for STB in STBs:
        STB.set_eco()
        STB.press("power")
    name="DAILY_REBOOT_ECO_ACTIVE.csv"
    logger(end_of_test_time(1),name,powerbricks)
    for STB in STBs:
        STB.set_active()
        STB.press("power")
    logger(end_of_test_time(2),name,powerbricks)
    send_email(name,powerbricks)

def TITAN_ONLY_ACTIVE(TITAN, powerbrick, ethernet):
    TITAN.set_active()
    TITAN.toggle_tuners()
    TITAN.press("power")
    #TITAN.toggle_wireless()
    ethernet.turnoff()
    TITAN.sat_feeds(0)
    name="TITAN_ONLY_ACTIVE.csv"
    logger(end_of_test_time(2),name,powerbrick)
    send_email(name,smartplug)
    TITAN.sat_feeds(1)
    ethernet.turnon()
    TITAN.toggle_tuners()
    #TITAN.toggle_wireless()

def TITAN_ONLY_NONE(TITAN, powerbrick,ethernet):
    TITAN.set_none()
    TITAN.toggle_tuners()
    TITAN.press("power")
    #TITAN.toggle_wireless()
    ethernet.turnoff()
    TITAN.sat_feeds(0)
    name="TITAN_ONLY_NONE.csv"
    logger(end_of_test_time(2),name,powerbrick)
    send_email(name,powerbrick)
    TITAN.sat_feeds(1)
    ethernet.turnon()
    TITAN.toggle_tuners()
    #TITAN.toggle_wireless() 

def RTNSS_DAILY_POWER_CYCLE_3_NIGHT(STBs, powerbricks):
    for STB in STBs:
        STB.set_active()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_DAILY_POWER_CYCLE_3_NIGHT.csv"
    error=logger(end_of_test_time(3),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_DAILY_3_NIGHT(STBs, powerbricks):
    for STB in STBs:
        STB.set_active()
        STB.sat_feeds(0)
    name="RTNSS_DAILY_3_NIGHT.csv"
    logger(end_of_test_time(3),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_ECO_OVERNIGHT(STBs, powerbricks):
    for STB in STBs:
        STB.set_eco()
        STB.sat_feeds(0)
    name="RTNSS_ECO_OVERNIGHT.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_ECO_OVERNIGHT_REBOOT(STBs, powerbricks): 
    for STB in STBs:
        STB.set_eco()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_ECO_OVERNIGHT_REBOOT.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_NONE_OVERNIGHT_REBOOT(STBs, powerbricks):
    for STB in STBs:
        STB.set_none()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_NONE_OVERNIGHT_REBOOT.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_NONE_OVERNIGHT(STBs, powerbricks):
    for STB in STBs:
        STB.set_none()
        STB.sat_feeds(0)
    name="RTNSS_NONE_OVERNIGHT.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)
    for STB in STBs:
        STB.sat_feeds(1)

def OVERNIGHT_NONE(STBs, powerbricks):
    for STB in STBs:
        STB.set_none()
    n="OVERNIGHT_NONE.csv"
    logger(end_of_test_time(1),n,powerbricks)
    send_email(n,powerbricks)

def OVERNIGHT_ACTIVE(STBs, powerbricks):
    for STB in STBs:
        STB.set_active()
    name="OVERNIGHT_ACTIVE.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)

def OVERNIGHT_ECO(STBs, powerbricks):
    for STB in STBs:
        STB.set_eco()
    name="OVERNIGHT_ECO.csv"
    logger(end_of_test_time(1),name,powerbricks)
    send_email(name,powerbricks)
#main
       


DTH=49160
SOIP=5800

#define STBs
TITAN=sky.STB('TITAN','192.168.1.107', DTH, 2, 3)
XWING=sky.STB('XWING','192.168.1.108', DTH, 4, 5)
D1=sky.STB('D1','192.168.1.131', DTH, 6, 7)
V2=sky.STB('V2','192.168.1.104', DTH, 8, 9)

#define powerbricks
TITAN_brick=sky.powerbrick('TITAN', '192.168.1.117')
V2_brick=sky.powerbrick('V2','192.168.109')
XWING_brick=sky.powerbrick('XWING','192.168.1.125')
D1_brick=sky.powerbrick('D1','192.168.1.118')


ethernet=sky.network_switch('192.168.1.123')#ethernet smart plug IP address


STBs = [XWING, V2, D1, TITAN]
powerbricks = [XWING_brick, V2_brick, D1_brick, TITAN_brick]


for STB in STBs: #wakeup boxes
    STB.sat_feeds(1)
    STB.press("home home home home")

#list of tests

OVERNIGHT_ECO(STBs, powerbricks)
OVERNIGHT_ACTIVE(STBs, powerbricks)
OVERNIGHT_NONE(STBs, powerbricks)
RTNSS_NONE_OVERNIGHT(STBs, powerbricks)
RTNSS_NONE_OVERNIGHT_REBOOT(STBs, powerbricks)
RTNSS_ECO_OVERNIGHT_REBOOT(STBs, powerbricks)
RTNSS_ECO_OVERNIGHT(STBs, powerbricks)
RTNSS_DAILY_3_NIGHT(STBs, powerbricks)
RTNSS_DAILY_POWER_CYCLE_3_NIGHT(STBs, powerbricks)
TITAN_ONLY_NONE(TITAN, [TITAN_brick])
TITAN_ONLY_ACTIVE(TITAN, [TITAN_brick])
DAILY_REBOOT_ECO_ACTIVE(STBs, powerbricks)
DAILY_REBOOT_NONE(STBs, powerbricks)
DAILY_REBOOT_ECO_NONE(STBs,  powerbricks)
DAILY_REBOOT_ACTIVE(STBs, powerbricks)


