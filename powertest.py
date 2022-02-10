import os, time, os.path, smtplib, ssl
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sky

#PROCESS FUNCTIONS
def array_or(a1,a2): #OR logic function between the Nth element of two error arrays
    if len(a1)>len(a2):#if the arrays are different length, the resultant array is the length of the smaller array
        a=[0 for i in range(len(a2))]
    else:
        a=[0 for i in range(len(a1))]
    for i in range(len(a)):
        if a1[i] or a2[i]: #if either ith element is set, that value is copied to the new array
            if a1[i]>0:
                a[i]=a1[i]
            else:
                a[i]=a2[i]
    return a #new array returned

def end_of_test_time(d): #Length of the test, in days, is taken as an argument and the date of the end of the test is returned, all tests finish at 7am 
    t1=datetime.now()
    t2=(datetime.now()+timedelta(days=d))
    t2=t2.replace(hour=7, minute=0, second=0, microsecond=0)
    return t2



def logger(end_time,test,smartplugs): #logs power for all platforms at the same time creating a different csv file for each
    error = [0 for i in range(len(STBs))] #setup error array
    failures=[0 for i in range(len(STBs))] #counts successive failures to connect to a smartplug for each platform
    exit_case=[1 for i in range(len(smartplugs))]#case when to stop logging power (unable to connect to all smartplugs)
    print("logging power...")
    while((datetime.now()<end_time)): #loop executed until the end of time/date
        n=0
        for plug in smartplugs:
            if error[n]==0:#only logs on the smartplugs that do not have error flags
                name=str(plug.platform+"_"+test) #change
                f = open(name, "a") #appends powerlog file
                power=plug.power()
                f.write(power)
                if power=="":
                    failures[n] = failures[n]+1 #increments consecutive failures on the failed platform 
                    if failures[n]==120: #if 120 successive failures to retrieve power, marks an error and stops recording
                        error[n]=1
                        print("connection failed ",plug.platform)
            elif error == exit_case: #if all platforms have failed, logging ceases and exits
                return error
            n=n+1
        time.sleep(0.5)
    return error


def send_email(error,name,smartplugs): #sends four emails with test results from each platform
    n=0
    print("sending email...")
    for plug in smartplugs:
        name2=str(plug.platform+"_"+name)
        subject = "Test results"
        if(error[n]==0):
                body = "Results attached as CSV file" #message returned if the test has been conducted successfully
        if(error[n]==1):
                body = "test failed" #message returned if the test has failed to be conducted
        sender_email = "automatedtests.sky@gmail.com"
        receiver_email = RECIEVER_EMAIL
        password = PASSWORD
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject 
        message.attach(MIMEText(body, "plain")) # Add body to email
        filename = (name2)  # In same directory as script
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
            print("couldn't send email ", plug.platform)
        n=n+1


#TESTS
def DAILY_REBOOT_ACTIVE(STBs, smartplugs):
    for STB in STBs:
        STB.set_active()
        STB.press("power")
    name="DAILY_REBOOT_ACTIVE.csv"
    error=logger(end_of_test_time(3),name,smartplugs)
    send_email(error,name,smartplugs)

def DAILY_REBOOT_NONE(STBs, smartplugs):
    for STB in STBs:
        STB.set_none() 
        STB.press("power")
    name="DAILY_REBOOT_NONE.csv"
    error=logger(end_of_test_time(3),name,smartplugs)
    send_email(error,name,smartplugs)

def DAILY_REBOOT_ECO_NONE(STBs, smartplugs):
    for STB in STBs:
        STB.set_eco()
        STB.press()
    name="DAILY_REBOOT_ECO_NONE.csv"
    error=logger(end_of_test_time(1),name)
    if(error!=[1 for x in range(len(smartplugs))]):
        for STB in STBs:
            STB.set_none()
            STB.press("power")
        error2=logger(end_of_test_time(2),name,smartplugs)
    error=array_or(error,error2)
    send_email(error,name,smartplugs)

def DAILY_REBOOT_ECO_ACTIVE(STBs, smartplugs):
    for STB in STBs:
        STB.set_eco()
        STB.press("power")
    name="DAILY_REBOOT_ECO_ACTIVE.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    if(error!=[1 for x in range(len(STBs))]):
        for STB in STBs:
            STB.set_active()
            STB.press("power")
        error2=logger(end_of_test_time(2),name,smartplugs)
    error=array_or(error,error2)
    send_email(error,name,smartplugs)

def TITAN_ONLY_ACTIVE(TITAN, smartplug, ethernet):
    TITAN.set_active()
    TITAN.toggle_tuners()
    TITAN.press("power")
    #TITAN.toggle_wireless()
    ethernet.turnoff()
    TITAN.sat_feeds(0)
    name="TITAN_ONLY_ACTIVE.csv"
    error=logger(end_of_test_time(2),name,smartplug)
    send_email(error,name,smartplug)
    TITAN.sat_feeds(1)
    ethernet.turnon()
    TITAN.toggle_tuners()
    #TITAN.toggle_wireless()

def TITAN_ONLY_NONE(TITAN, smartplug,ethernet):
    TITAN.set_none()
    TITAN.toggle_tuners()
    TITAN.press("power")
    #TITAN.toggle_wireless()
    ethernet.turnoff()
    TITAN.sat_feeds(0)
    name="TITAN_ONLY_NONE.csv"
    error=logger(end_of_test_time(2),name,smartplugs)
    send_email(error,name,smartplugs)
    TITAN.sat_feeds(1)
    ethernet.turnon()
    TITAN.toggle_tuners()
    #TITAN.toggle_wireless() 

def RTNSS_DAILY_POWER_CYCLE_3_NIGHT(STBs, smartplugs):
    for STB in STBs:
        STB.set_active()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_DAILY_POWER_CYCLE_3_NIGHT.csv"
    error=logger(end_of_test_time(3),name,smartplugs)
    send_email(error, name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_DAILY_3_NIGHT(STBs, smartplugs):
    for STB in STBs:
        STB.set_active()
        STB.sat_feeds(0)
    name="RTNSS_DAILY_3_NIGHT.csv"
    error=logger(end_of_test_time(3),name,smartplugs)
    send_email(error,name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_ECO_OVERNIGHT(STBs, smartplugs):
    for STB in STBs:
        STB.set_eco()
        STB.sat_feeds(0)
    name="RTNSS_ECO_OVERNIGHT.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_ECO_OVERNIGHT_REBOOT(STBs, smartplugs): 
    for STB in STBs:
        STB.set_eco()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_ECO_OVERNIGHT_REBOOT.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_NONE_OVERNIGHT_REBOOT(STBs, smartplugs):
    for STB in STBs:
        STB.set_none()
        STB.sat_feeds(0)
        STB.reboot()
    name="RTNSS_NONE_OVERNIGHT_REBOOT.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def RTNSS_NONE_OVERNIGHT(STBs, smartplugs):
    for STB in STBs:
        STB.set_none()
        STB.sat_feeds(0)
    name="RTNSS_NONE_OVERNIGHT.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)
    for STB in STBs:
        STB.sat_feeds(1)

def OVERNIGHT_NONE(STBs, smartplugs):
    for STB in STBs:
        STB.set_none()
    n="OVERNIGHT_NONE.csv"
    error=logger(end_of_test_time(1),n,smartplugs)
    send_email(error,n,smartplugs)

def OVERNIGHT_ACTIVE(STBs, smartplugs):
    for STB in STBs:
        STB.set_active()
    name="OVERNIGHT_ACTIVE.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)

def OVERNIGHT_ECO(STBs, smartplugs):
    for STB in STBs:
        STB.set_eco()
    name="OVERNIGHT_ECO.csv"
    error=logger(end_of_test_time(1),name,smartplugs)
    send_email(error,name,smartplugs)
#main
       
#os.system("npm install sky-remote") 

DTH=49160
SOIP=5800

#define STBs
TITAN=sky.STB('TITAN','192.168.1.107', DTH, 2, 3)
XWING=sky.STB('XWING','192.168.1.108', DTH, 4, 5)
D1=sky.STB('D1','192.168.1.131', DTH, 6, 7)
V2=sky.STB('V2','192.168.1.104', DTH, 8, 9)

#define smartplugs
TITAN_SP=sky.plug('TITAN', '192.168.1.117')
V2_SP=sky.plug('V2','192.168.109')
XWING_SP=sky.plug('XWING','192.168.1.125')#not correct
D1_SP=sky.plug('D1','192.168.1.118')


ethernet=sky.network_switch('192.168.1.123')#ethernet smart plug IP address

smartplug = [TITAN_SP]

STBs = [XWING, V2,D1, TITAN]
smartplugs = [XWING_SP, V2_SP, D1_SP, TITAN_SP]


for STB in STBs: #wakeup boxes
    STB.sat_feeds(1)
    STB.press("home home home home")

#list of tests

OVERNIGHT_ECO(STBs, smartplugs)
OVERNIGHT_ACTIVE(STBs, smartplugs)
OVERNIGHT_NONE(STBs, smartplugs)
RTNSS_NONE_OVERNIGHT(STBs, smartplugs)
RTNSS_NONE_OVERNIGHT_REBOOT(STBs, smartplugs)
RTNSS_ECO_OVERNIGHT_REBOOT(STBs, smartplugs)
RTNSS_ECO_OVERNIGHT(STBs, smartplugs)
RTNSS_DAILY_3_NIGHT(STBs, smartplugs)
RTNSS_DAILY_POWER_CYCLE_3_NIGHT(STBs, smartplugs)
TITAN_ONLY_NONE(TITAN, smartplug)
TITAN_ONLY_ACTIVE(TITAN, smartplug)
DAILY_REBOOT_ECO_ACTIVE(STBs, smartplugs)
DAILY_REBOOT_NONE(STBs, smartplugs)
DAILY_REBOOT_ECO_NONE(STBs, smartplugs)
DAILY_REBOOT_ACTIVE(STBs, smartplugs)


