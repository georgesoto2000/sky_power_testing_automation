import time, os, requests
from datetime import datetime
from pyHS100 import SmartPlug
import RPi.GPIO as GPIO 

class STB: #STB class
    #class atributes
    requirements="Node.js required"
    DTH_VNC_port=49160
    SOIP_VNC_port=5800
    platform=""
    def __init__(self, platform, IP, vnc_port,sat1, sat2): #initilise STB object with IP address of box and VNC port
        self.IP=IP
        self.vnc_port=vnc_port
        self.sat1=sat1
        self.sat2=sat2
        self.platform=platform

    def press(self,string): #emulate remote with string of buton presses
        with open('sky-remote.js','r') as file: #rewrite VNC port on sky-remote module for different devices
            lines=file.readlines()
            lines[68]="SkyRemote.SKY_Q = "+str(self.vnc_port)+";"
        with open("sky-remote.js",'w') as file:
            file.writelines(lines)
        string=string.split()
        n=0
        for command in string: #for each button press, write it into javascript file and execute it
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
    def wake(self): #checks if box is 'alive', if it doesn't wake after 5 minutes it breaks and prints and error. STBs can vary in time to reboot
        wake=0
        while True:
            self.press("home home home home")
            try:
                url="http://"+self.IP+":9005/as/action/ping" #throws error if box is not 'alive'
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

class network_switch(SmartPlug): 
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

class plug(SmartPlug): 
    def __init__(self,platform, IP):
        super().__init__(IP)
        self.platform=platform
    def power(self): #if connection is established, returns a line of time and power consumption to write to csv file
        try:
            power=self.current_consumption()
            x = datetime.now()
            string=str(x)+","+str(power)+"\n"
            return string
        except:
            string=""
            return string
        
        
    



        
    

