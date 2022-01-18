#bash automated tests
import RPi.GPIO as GPIO 
import numpy as np
import os, time
from pyHS100 import SmartPlug, Discover
import time
import os, os.path 
from datetime import datetime, timedelta
from struct import pack
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def secret_menu(): #Navigates to 001 Engineering Settings Menu
    send_command("home down down down down down down down down down down down 0 0 1 select")
def toggle_wireless():#Turns on/off 2.4GHz and 5GHz WiFi ports
    print("turning wireless on/off")
    secret_menu()
    send_command("down select select down select down down select")
def toggle_tuners(): #Turns on/off Set Top Box's (STB) Tuners
    print("turning tuners on/off")
    send_command("home down down down down down down down down down down down 8 8 6 3 7 select select select home backup")
def set_eco(): #Sets 'eco' power mode on STBs
    print("setting eco mode")
    send_command("home home down down down down down down down down down down down select down down down down select down down down down select right down down select left select home backup")
def set_none(): #Sets 'none' power mode on STBs
    print("setting none mode")
    send_command("home home down down down down down down down down down down down select down down down down select down down down down select right down down up up select left select home backup") 
def set_active(): #Sets 'active' power mode on STBs
    print("setting active mode")
    send_command("home home down down down down down down down down down down down select down down down down select down down down down select right down down up select left select home backup")

def titan_sat_feed(x): #Turns satellite feeds on/off to the Titan STB 
    sat_1(x) #when the argument is 0, satellite feeds are turned off. When 1 is the argument, satellite feeds are turned on 
    sat_2(x)
    if x==1:
        print("Titan satellite feeds on")
    else:
        print("Titan satellite feeds off")

def xwing_sat_feed(x): #Turns satellite feeds on/off to the Xwing STB 
    sat_3(x) #when the argument is 0, satellite feeds are turned off. When 1 is the argument, satellite feeds are turned on 
    sat_4(x)
    if x==1:
        print("Xwing satellite feeds on")
    else:
        print("Xwing satellite feeds off")
    
def d1_sat_feed(x): #Turns satellite feeds on/off to the D1 STB 
    sat_5(x) #when the argument is 0, satellite feeds are turned off. When 1 is the argument, satellite feeds are turned on 
    sat_6(x)
    if x==1:
        print("D1 satellite feeds on")
    else:
        print("D1 satellite feeds off")

def v2_sat_feed(x): #Turns satellite feeds on/off to the V2 STB 
    sat_7(x) #when the argument is 0, satellite feeds are turned off. When 1 is the argument, satellite feeds are turned on 
    sat_8(x)
    if x==1:
        print("V2 satellite feeds on")
    else:
        print("V2 satellite feeds off")

def sat_1(x): #Turns satellite feed 1 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(2, GPIO.OUT)  #set GPIO2 as an o/p          
    GPIO.output(2, x) # Set Vctrl on/off 

def sat_2(x): #Turns satellite feed 2 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(3, GPIO.OUT)  #set GPIO3 as an o/p           
    GPIO.output(3, x) #Vctrl on/off 

def sat_3(x): #Turns satellite feed 3 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(4, GPIO.OUT) #set GPIO4 as an o/p         
    GPIO.output(4, x) #Vctrl on/off 

def sat_4(x): #Turns satellite feed 4 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(5, GPIO.OUT)  #set GPIO5 as an o/p          
    GPIO.output(5, x) #Vctrl on/off

def sat_5(x): #Turns satellite feed 5 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(6, GPIO.OUT)  #set GPIO6 as an o/p          
    GPIO.output(6, x) #Vctrl on/off 

def sat_6(x): #Turns satellite feed 6 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(7, GPIO.OUT)  #set GPIO7 as an o/p           
    GPIO.output(7, x) #Vctrl on/off 

def sat_7(x): #Turns satellite feed 7 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(8, GPIO.OUT)  #set GPIO8 as an o/p          
    GPIO.output(8, x) #Vctrl on/off 

def sat_8(x): #Turns satellite feed 8 on/off
    GPIO.setmode(GPIO.BCM)         
    GPIO.setup(9, GPIO.OUT)  #set GPIO9 as an o/p           
    GPIO.output(9, x) #Vctrl on/off

def sat_feeds(x): #turns on/off all satellite feeds
    titan_sat_feed(x)
    xwing_sat_feed(x)
    d1_sat_feed(x)
    v2_sat_feed(x)

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

def turn_off_ethernet(): #Turns off network switch to STBs, disabling ethernet connection to STBs
    ETHERNET=SmartPlug(ethernet)
    error=0
    try:
        ETHERNET.turn_off() #If connection cannot be made to smartplug and error is thrown
        print("Ethernet off")
    except:
        print("Failed to connect")
        error=1
    return error
def turn_on_ethernet(): #Turns on network switch to STBs, enabling ethernet connection to STBs
    ETHERNET=SmartPlug(ethernet)
    error=0
    try:
        ETHERNET.turn_on()
        print("Ethernet on")
    except:
        print("failed to connect")
        error=1
    time.sleep(200) #Waits until connection via ethernet is established before proceeding with next steps in code
    return error

def power_cycle(): #power cycles each STB using its smartplug, if it fails to connect it appends the error array to mark the error
    error=[0 for i in range(len(STBs))]
    n=0
    for platform in smartplugs:
            ip=str(smartplugs[platform])
            try:
                plug = SmartPlug(ip)
                plug.turn_on()
                time.sleep(1)
                plug.turn_off()
                time.sleep(1)
                plug.turn_on()
                error[n]=0
                print("power cycling STBs")
            except:
                error[n]=1
            n=n+1
    time.sleep(200) #wait for STB to reboot before proceeding
    return error #return error array

def end_of_test_time(d): #Length of the test, in days, is taken as an argument and the date of the end of the test is returned, all tests finish at 7am 
    t1=datetime.now()
    t2=(datetime.now()+timedelta(days=d))
    t2=t2.replace(hour=7, minute=0, second=0, microsecond=0)
    return t2

def send_command(string): #uses sky-remote Node.js module to transmit bytes to port 49160, emulating remote control button presses
    string=string.split()
    for platform in STBs: #sends presses to all platforms
        n=0
        for command in string:
            IP=str(STBs[platform])
            filename=platform+"_"+str(n)+".js"
            f1 = open(filename,"w+")
            f1.write("var SkyRemote = require('sky-remote');\nvar RCU = new SkyRemote('"+IP+"');\n")
            f1.write("RCU.press('"+command+"');")
            f1.flush()
            f1.close()
            js_call=str("node "+platform+"_"+str(n)+".js")
            os.system(js_call)
            n=n+1
            os.remove(filename)
            time.sleep(1) 
def clear_file(name): #clears power logging files before a new test starts
    for platform in smartplugs:
        name=platform+"_"+name
        print(name)
        f=open(name,"w")
        f.close
def logger(end_time,test): #logs power for all platforms at the same time creating a different csv file for each
    error = [0 for i in range(len(STBs))] #setup error array
    failures=[0 for i in range(len(STBs))] #counts successive failures to connect to a smartplug for each platform
    exit_case=[1 for i in range(len(STBs))]#case when to stop logging power (unable to connect to all smartplugs)
    print("logging power...")
    clear_file(test)
    while((datetime.now()<end_time)): #loop executed until the end of time/date
        n=0
        for platform in smartplugs:
            if error[n]==0:#only logs on the smartplugs that do not have error flags
                name=str(platform+"_"+test)
                ip=str(smartplugs[platform])
                f = open(name, "a") #appends powerlog file
                try:
                    plug = SmartPlug(ip)
                    x = datetime.now() #takes instantaneous power and casts to string
                    power=plug.current_consumption()
                    f.write(str(x)) #writes data to csv file
                    f.write(", ")
                    f.write(str(power))
                    f.write("\n")
                    f.flush()
                    f.close()
                    failures[n]=0 #power has been successfully retrieved, so reset consecutive failures to 0
                except:
                    f.close()
                    failures[n] = failures[n]+1 #increments consecutive failures on the failed platform 
                    print("connection failed ",platform)
                    print(failures[n]," out of 120")
                    if failures[n]==120: #if 120 successive failures to retrieve power, marks an error and stops recording
                        error[n]=1
                time.sleep(1)
            if error == exit_case: #if all platforms have failed, logging ceases and exits
                return error
            n=n+1
    return error

def send_email(error,name): #sends four emails with test results from each platform
    n=0
    print("sending email...")
    for platform in STBs:
        name2=str(platform+"_"+name)
        subject = "Test results"
        if(error[n]==0):
                body = "Results attached as CSV file" #message returned if the test has been conducted successfully
        if(error[n]==1):
                body = "test failed" #message returned if the test has failed to be conducted
        sender_email = "automatedtests.sky@gmail.com"
        receiver_email = "george.soto@sky.uk"
        password = "Tester1234"
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
            print("couldn't send email ", platform)
        n=n+1

def DAILY_REBOOT_ACTIVE():
    set_active()
    send_command("power")
    name="DAILY_REBOOT_ACTIVE.csv"
    error=logger(end_of_test_time(3),name)
    send_email(error,name)
def DAILY_REBOOT_NONE():
    set_none() 
    name="DAILY_REBOOT_NONE.csv"
    send_command("power")
    error=logger(end_of_test_time(3),name)
    send_email(error,name)
def DAILY_REBOOT_ECO_NONE():
    set_eco()
    name="DAILY_REBOOT_ECO_NONE.csv"
    send_command("power")
    error=logger(end_of_test_time(1),name)
    if(error!=[1 for x in range(len(STBs))]):
        set_none()
        error2=logger(end_of_test_time(2),name)
    error=array_or(error,error2)
    send_email(error,name)
def DAILY_REBOOT_ECO_ACTIVE():
    set_eco()
    name="DAILY_REBOOT_ECO_ACTIVE.csv"
    send_command("power")
    error=logger(end_of_test_time(1),name)
    if(error!=[1 for x in range(len(STBs))]):
        set_active()
        error2=logger(end_of_test_time(2),name)
    error=array_or(error,error2)
    send_email(error,name)
def TITAN_ONLY_ACTIVE():
    set_active()
    toggle_tuners()
    send_command("power")
    #toggle_wireless()
    turn_off_ethernet()
    titan_sat_feed(0)
    name="TITAN_ONLY_ACTIVE.csv"
    error=logger(end_of_test_time(2),name)
    send_email(error,name)
    titan_sat_feed(1)
    turn_on_ethernet()
    toggle_tuners()
    #toggle_wireless()
def TITAN_ONLY_NONE():
    set_none()
    toggle_tuners()
    send_command("power")
    #toggle_wireless()
    turn_off_ethernet()
    titan_sat_feed(0)
    name="TITAN_ONLY_NONE.csv"
    error=logger(end_of_test_time(2),name)
    send_email(error,name)
    titan_sat_feed(1)
    turn_on_ethernet()
    toggle_tuners()
    #toggle_wireless() 
def RTNSS_DAILY_POWER_CYCLE_3_NIGHT():
    set_active()
    sat_feeds(0)
    name="RTNSS_DAILY_POWER_CYCLE_3_NIGHT.csv"
    error=power_cycle()
    if error!=[1 for x in range(len(STBs))]:
            error2=logger(end_of_test_time(3),name)
    error=array_or(error,error2)
    send_email(error, name)
    sat_feeds(1)
def RTNSS_DAILY_3_NIGHT():
    set_active()
    sat_feeds(0)
    name="RTNSS_DAILY_3_NIGHT.csv"
    error=logger(end_of_test_time(3),name)
    send_email(error,name)
    sat_feeds(1)

def RTNSS_ECO_OVERNIGHT():
    set_eco()
    name="RTNSS_ECO_OVERNIGHT.csv"
    sat_feeds(0)
    error=logger(end_of_test_time(1),name)
    send_email(error,name)
    sat_feeds(1)

def RTNSS_ECO_OVERNIGHT_REBOOT(): 
    set_eco()
    sat_feeds(0)
    name="RTNSS_ECO_OVERNIGHT_REBOOT.csv"
    error=power_cycle()
    if error!=[1 for x in range(len(STBs))]:
        error2=logger(end_of_test_time(1),name)
    error=array_or(error,error2)
    send_email(error,name)
    sat_feeds(1)

def RTNSS_NONE_OVERNIGHT_REBOOT():
    set_none()
    sat_feeds(0)
    name="RTNSS_NONE_OVERNIGHT_REBOOT.csv"
    error=power_cycle()
    if error!=[1 for x in range(len(STBs))]:
        error2=logger(end_of_test_time(1),name)
    error=array_or(error,error2)
    send_email(error,name)
    sat_feeds(1)
def RTNSS_NONE_OVERNIGHT():
    set_none()
    sat_feeds(0)
    name="RTNSS_NONE_OVERNIGHT.csv"
    error=logger(end_of_test_time(1),name)
    send_email(error,name)
    sat_feeds(1)
def OVERNIGHT_NONE():
    set_none()
    n="OVERNIGHT_NONE.csv"
    error=logger(end_of_test_time(1),n)
    send_email(error,n)
def OVERNIGHT_ACTIVE():
    set_active()
    name="OVERNIGHT_ACTIVE.csv"
    error=logger(end_of_test_time(1),name)
    send_email(error,name)
def OVERNIGHT_ECO():
    set_eco()
    name="OVERNIGHT_ECO.csv"
    error=logger(end_of_test_time(1),name)
    send_email(error,name)

#main
       
#os.system("npm install sky-remote") 
sat_feeds(1)
ethernet=str('192.168.1.105') #ethernet smart plug IP address
STBs = {'TITAN':'192.168.1.107', 'V2':'192.168.1.104','XWING':'192.168.1.130', 'D1':'192.168.1.131'} #dictionary of platforms' IP addresses
smartplugs = {'TITAN':'192.168.1.117', 'V2':'192.168.119','XWING':'192.168.1.125','D1':'192.168.1.118'}#dictionary of smart plugs' IP addresses

#dictionaries to be used for 'TITAN_ONLY' tests
#STBs = {'TITAN':'192.168.1.107'} 
#smartplugs = {'TITAN':'192.168.1.117'} 

send_command("home home home") #wake STBs

#list of tests

#OVERNIGHT_ECO()
#OVERNIGHT_ACTIVE()
#OVERNIGHT_NONE()
#RTNSS_NONE_OVERNIGHT()
#RTNSS_NONE_OVERNIGHT_REBOOT()
#RTNSS_ECO_OVERNIGHT_REBOOT()
#RTNSS_ECO_OVERNIGHT()
#RTNSS_DAILY_3_NIGHT()
#RTNSS_DAILY_POWER_CYCLE_3_NIGHT()
#TITAN_ONLY_NONE()
#TITAN_ONLY_ACTIVE()
#DAILY_REBOOT_ECO_ACTIVE()
#DAILY_REBOOT_NONE()
#DAILY_REBOOT_ECO_NONE()
#DAILY_REBOOT_ACTIVE()


