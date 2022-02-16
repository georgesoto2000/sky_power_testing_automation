import time, os, requests
from datetime import datetime
from pyHS100 import SmartPlug
import RPi.GPIO as GPIO 
from telnetlib import Telnet

class STB: #STB class
    #class atributes
    requirements="Node.js required"
    DTH_VNC_port=49160
    SOIP_VNC_port=5800
    def __init__(self, platform, IP, vnc_port,sat1, sat2): #initilise STB object with IP address of box and VNC port
        self.IP=IP
        self.vnc_port=vnc_port
        self.sat1=sat1
        self.sat2=sat2
        self.platform=platform

    def press(self,string): #emulate remote with string of buton presses
        with open('sky-remote.js','r') as file: #rewrite VNC port on sky-remote module
            lines=file.readlines()
            lines[68]="SkyRemote.SKY_Q = "+str(self.vnc_port)+";"
        with open("sky-remote.js",'w') as file:
            file.writelines(lines)
        string=string.split()
        n=0
        for command in string: #for each command, write it into javascript file and execute it
            filename=self.platform+"_"+str(n)+".js"
            f1 = open(filename,"w+")
            f1.write("var SkyRemote = require('sky-remote');\nvar RCU = new SkyRemote('"+self.IP+"');\n")
            f1.write("RCU.press('"+command+"');")
            f1.flush()
            f1.close()
            js_call=str("node "+filename)
            os.system(js_call)
            os.remove(filename)
            n=n+1
            time.sleep(1)

    def reboot(self):#reboots box with API call
        print("rebooting ",self.platform)
        url="http://"+self.IP+":9005/as/system/action/reset?type=reboot"
        requests.post(url)
        time.sleep(30)
        self.wake()
    def wake(self):
        wake=0
        while True:
            self.press("home home home home")
            try:
                url="http://"+self.IP+":9005/as/action/ping"
                requests.post(url)
                print(self.platform, ": On")
                self.press("home home home home")
                break
            except:
                wake=wake+1
                if wake>10:
                    print("failed to reboot")
                    break
                else:
                    time.sleep(60)
        

    def secret_menu(self): #open engineering menu through EPG
        self.press("home down down down down down down down down down down down 0 0 1 select")
    def toggle_wireless(self):#Turns on/off 2.4GHz and 5GHz WiFi ports
        print("turning wireless on/off ",self.platform)
        self.secret_menu()
        self.press("down select select down select down down select")

    def toggle_tuners(self): #Turns on/off Set Top Box's (STB) Tuners
        print("turning tuners on/off ",self.platform)
        self.press("home down down down down down down down down down down down 8 8 6 3 7 select select select home backup")

    def set_eco(self): #Sets 'eco' power mode on STBs
        print("setting eco mode ",self.platform)
        self.press("home home down down down down down down down down down down down select down down down down select down down down down select right down down select left select home backup")

    def set_none(self): #Sets 'none' power mode on STBs
        print("setting none mode ",self.platform)
        self.press("home home down down down down down down down down down down down select down down down down select down down down down select right down down up up select left select home backup") 

    def set_active(self): #Sets 'active' power mode on STBs
        print("setting active mode ",self.platform)
        self.press("home home down down down down down down down down down down down select down down down down select down down down down select right down down up select left select home backup")

    def sat_feeds(self,x): #Turns satellite feed 1 on/off
        GPIO.setmode(GPIO.BCM)         
        GPIO.setup(self.sat1, GPIO.OUT)  #set GPIO2 as an o/p          
        GPIO.setup(self.sat2, GPIO.OUT)      
        GPIO.output(self.sat1, x) # Set Vctrl on/off 
        GPIO.output(self.sat2, x)
        print("sat feeds ",x,self.platform)

    def negative_test(self):
        tn=Telnet(self.IP)
        user="darwin"
        password="themoose"
        tn.read_until(b"bskyb-xwing412 login:")
        tn.write(user.encode("ascii")+b"\n")
        tn.read_until(b"Password:")
        tn.write(password.encode("ascii")+b"\n")
        tn.write("cd /mnt/nds".encode("ascii")+b"\n")
        tn.write("ls".encode("ascii")+b"\n")
        files=str(tn.read_until(b"dev_19"))
        dev=["dev_11","dev_12","dev_13","dev_14","dev_15", "dev_16","dev_17","dev_18","dev_19"] #list of files in directory
        for devs in dev:
            command="cd "+devs
            tn.write(command.encode("ascii")+b"\n")
            tn.write("ls".encode("ascii")+b"\n")
            tn.read_until(b"-sh-3.2#")
            tn.write(("cd part_0").encode("ascii")+b"\n")
            tn.read_until(b"-sh-3.2#")
            tn.write("ls LOG".encode("ascii")+b"\n")
            file=tn.read_until(b"directory",timeout=1)
            file=file.split()
            flag=0
            for i in file:
                if i==b'directory':
                    flag=1
            if flag==0:
                tn.write("tail -F LOG | grep -i asid_fizzy_watermark.c".encode("ascii")+b"\n")
                file=tn.read_until(b"Avg")
                tn.close()
                file=file.split()
                for i in range(0,len(file)):
                    if file[i]==b"Index":
                        if file[i+3]==b'(0),':
                            return True
                        else:
                            return False
                break
            tn.write("cd ..".encode("ascii")+b"\n")
            tn.write("cd ..".encode("ascii")+b"\n")
        print("failed to find LOG directory")
        tn.close
        return False

    def play_netflix(self): 
        url1="http://"+self.IP+":9005/as/apps"
        reply=requests.get(url1).json()
        for i in (reply["apps"]):
            if i["appId"]=="Netflix":
                url="http://"+self.IP+":9005/as/apps/action/launch"
                file=requests.post(url, data=None, params={"appId":"Netflix"})
                time.sleep(20)
                self.press("select")
                return True
        return False
    def play_youtube(self):
        url1="http://"+self.IP+":9005/as/apps"
        reply=requests.get(url1).json()
        for i in (reply["apps"]):
            if i["appId"]=="YouTube":
                url="http://"+self.IP+":9005/as/apps/action/launch"
                file=requests.post(url, data=None, params={"appId":"YouTube"})
                time.sleep(20)
                self.press("select")
                return True
        return False
    def play_sky_boxsets(self):
        self.press("home")
    def play_sky_store(self):
        self.press("home")
    def play_sky_cinema(self):
        self.press("home")
class network_switch(SmartPlug): #change to be polymorphic?
    def __init__(self,IP):
        super().__init__(IP)
    def turnoff(self):
        error=0
        try:
            self.turn_off() #If connection cannot be made to smartplug and error is thrown
            print("Ethernet off")
        except:
            print("Failed to connect")
            error=1
        return error
    def turnon(self):
        error=0
        try:
            self.turn_on() #If connection cannot be made to smartplug and error is thrown
            print("Ethernet on")
            time.sleep(400)
        except:
            print("Failed to connect")
            error=1
        return error

class powerbrick(): 
    def __init__(self,platform, IP):
        self.platform=platform
        self.IP=IP
    def get_power(self):
        try:
            tn=Telnet(self.ip)
            command="GET ALL\r\n"
            file=tn.read_until(b"#",timeout=1)
            time.sleep(1)
            tn.write(command.encode("utf-8"))
            power=str(tn.read_until(b"#",timeout=1))
            tn.close
            power=power[7:76]+"+\n"
            return str(power)
        except:
            print("failed to connect to powerbrick ", self.platform)
            return ""


        
        
    



        
    

