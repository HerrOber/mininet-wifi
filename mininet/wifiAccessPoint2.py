import os
import subprocess
import time
import socket
import struct
import fcntl
import fileinput

from mininet.wifiParameters import wifiParameters
from mininet.wifiDevices import deviceDataRate
from mininet.log import info, debug

class accessPoint( object ):

    def __init__( self, ap, country_code=None, auth_algs=None, wpa=None, intf=None, wlan=None,
              wpa_key_mgmt=None, rsn_pairwise=None, wpa_passphrase=None, encrypt=None, 
              wep_key0=None, **params ):
        
        newname = str(ap)+'-'+str('wlan')
        self.renameIface(ap, intf, newname, wlan )
        self.getMacAddress(ap, wlan)
        self.start (ap, country_code, auth_algs, wpa, wlan,
              wpa_key_mgmt, rsn_pairwise, wpa_passphrase, encrypt, 
              wep_key0, **params)

    def renameIface( self, ap, intf, newname, wlan ):
        "Rename interface"
        newname = str(newname) + str(wlan)

        #print "11111111"
        #print('ifconfig %s down' % intf)
        ap.cmd('ifconfig %s down' % intf)
        #print('ip link set %s name %s' % (intf, newname))
        ap.cmd('ip link set %s name %s' % (intf, newname))
        #print('ifconfig %s up' % newname)   # this creates ap#-wlan0
        ap.cmd('ifconfig %s up' % newname)   # this creates ap#-wlan0
        #print(ap.cmd('ifconfig'))
        #print "22222222"
        """
        print('ifconfig %s down' % intf)
        os.system('ifconfig %s down' % intf)
        print('ip link set %s name %s' % (intf, newname))
        os.system('ip link set %s name %s' % (intf, newname))
        print('ifconfig %s up' % newname)   # this creates ap#-wlan0
        os.system('ifconfig %s up' % newname)   # this creates ap#-wlan0
        print(ap.cmd('ifconfig'))
        #print(os.system('ifconfig'))
        """
    
    def start(self, ap, country_code=None, auth_algs=None, wpa=None, wlan=None,
              wpa_key_mgmt=None, rsn_pairwise=None, wpa_passphrase=None, encrypt=None, 
              wep_key0=None, **params):
        """ Starts an Access Point """
        
        self.cmd = ("echo \'")
        self.cmd = self.cmd + ("interface=%s-wlan%s" % (ap, wlan)) # the interface used by the AP
        self.cmd = self.cmd + ("\ndriver=nl80211")
        self.cmd = self.cmd + ("\nssid=%s" % ap.ssid[0]) # the name of the AP
        
        
        if ap.mode == 'n' or ap.mode == 'ac'or ap.mode == 'a':
            self.cmd = self.cmd + ("\nhw_mode=g") 
        else:
            self.cmd = self.cmd + ("\nhw_mode=%s" % ap.mode) 
        self.cmd = self.cmd + ("\nchannel=%s" % ap.channel) # the channel to use 
        #if(ap.mode=="ac" or ap.mode=='a'):
        #   self.cmd = self.cmd + ("\nieee80211ac=1")
        self.cmd = self.cmd + ("\nwme_enabled=1") 
        self.cmd = self.cmd + ("\nwmm_enabled=1") 
        #if(ap.mode=="n" or ap.mode=="a"):
        #   self.cmd = self.cmd + ("\nieee80211n=1")
        #if(ap.mode=="n"):
        #   self.cmd = self.cmd + ("\nht_capab=[HT40+][SHORT-GI-40][DSSS_CCK-40]")
        
        if encrypt == 'wpa':
            wifiParameters.wpa_supplicantIsRunning = True
            self.cmd = self.cmd + ("\nauth_algs=%s" % auth_algs)
            self.cmd = self.cmd + ("\nwpa=%s" % wpa)
            self.cmd = self.cmd + ("\nwpa_key_mgmt=%s" % wpa_key_mgmt ) 
            self.cmd = self.cmd + ("\nwpa_passphrase=%s" % wpa_passphrase)                        
        elif encrypt == 'wpa2':
            wifiParameters.wpa_supplicantIsRunning = True
            self.cmd = self.cmd + ("\nauth_algs=%s" % auth_algs)
            self.cmd = self.cmd + ("\nwpa=%s" % wpa)
            self.cmd = self.cmd + ("\nwpa_key_mgmt=%s" % wpa_key_mgmt ) 
            self.cmd = self.cmd + ("\nrsn_pairwise=%s" % rsn_pairwise)  
            self.cmd = self.cmd + ("\nwpa_passphrase=%s" % wpa_passphrase)   
        elif encrypt == 'wep':
            self.cmd = self.cmd + ("\nauth_algs=%s" % auth_algs)
            self.cmd = self.cmd + ("\nwep_default_key=%s" % 0) 
            self.cmd = self.cmd + ("\nwep_key0=%s" % wep_key0)                         
                
        #Not used yet!
        if(country_code!=None):
            self.cmd = self.cmd + ("\ncountry_code=%s" % country_code) # the country code
        
        #elif(len(self.baseStationName)>self.countAP and len(self.baseStationName) != 1):
        #    """From AP2"""
        #    self.cmd = self.apcommand
            #self.cmd = self.cmd + "\n"
        #    self.cmd = self.cmd + ("\nbss=%s" % self.newapif[self.nextIface]) # the interface used by the AP
        #    if(self.ssid!=None):
        #        self.cmd = self.cmd + ("\nssid=%s" % self.ssid ) # the name of the AP
                #self.cmd = self.cmd + ("\nssid=%s" % self.ssid) # the name of the AP
        #    if(self.auth_algs!=None):
        #        self.cmd = self.cmd + ("\nauth_algs=%s" % self.auth_algs) # 1=wpa, 2=wep, 3=both
        #    if(self.wpa!=None):
        #        self.cmd = self.cmd + ("\nwpa=%s" % self.wpa) # WPA2 only
        #    if(self.wpa_key_mgmt!=None):
        #        self.cmd = self.cmd + ("\nwpa_key_mgmt=%s" % self.wpa_key_mgmt ) 
        #    if(self.rsn_pairwise!=None):
        #        self.cmd = self.cmd + ("\nrsn_pairwise=%s" % self.rsn_pairwise)  
        #    if(self.wpa_passphrase!=None):
        #        self.cmd = self.cmd + ("\nwpa_passphrase=%s" % self.wpa_passphrase)  
        #    self.countAP = len(self.baseStationName)
        #    self.apcommand = ""       
        self.APfile(self.cmd, ap, wlan) 
  
  
    def getMacAddress(self, ap, wlan):
        """ get Mac Address of any Interface """
        iface = str(ap) + '-wlan' + str(wlan)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        info = ap.cmd('ifconfig | grep %s' % iface).strip()
        mac = info.split('HWaddr' , 2)[1].strip()
        #info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', '%s'[:15]) % iface)
        #print "info %s" % (info)
        #mac = (''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1])
        #print "mac %s" % (mac)
        self.checkNetworkManager(mac)
        
    def checkNetworkManager(self, mac):
        """ add mac address inside of /etc/NetworkManager/NetworkManager.conf """
        self.printMac = False   
        unmatch = ""
        if(os.path.exists('/etc/NetworkManager/NetworkManager.conf')):
            if(os.path.isfile('/etc/NetworkManager/NetworkManager.conf')):
                self.resultIface = open('/etc/NetworkManager/NetworkManager.conf')
                lines=self.resultIface
        
            isNew=True
            for n in lines:
                if("unmanaged-devices" in n):
                    unmatch = n
                    echo = n
                    echo.replace(" ", "")
                    echo = echo[:-1]+";"
                    isNew = False
            if(isNew):
                os.system("echo '#' >> /etc/NetworkManager/NetworkManager.conf")
                unmatch = "#"
                echo = "[keyfile]\nunmanaged-devices="
            
            if mac not in unmatch:
                echo = echo + "mac:" + mac + ';'
                self.printMac = True
            
            if(self.printMac):
                for line in fileinput.input('/etc/NetworkManager/NetworkManager.conf', inplace=1): 
                    if(isNew):
                        if line.__contains__('#'): 
                            print line.replace(unmatch, echo)
                        else:
                            print line.rstrip()
                    else:
                        if line.__contains__('unmanaged-devices'): 
                            print line.replace(unmatch, echo)
                        else:
                            print line.rstrip()
                #necessary to add mac address before starting the ap
                time.sleep(2)
          
    @classmethod
    def apBridge(self, ap, iface):
        """ AP Bridge """  
        intf = str(ap)+'-'+'wlan'+str(iface)
        os.system("ovs-vsctl add-port %s %s" % (ap, intf))
        #ap.cmd("sh ~/Applications/coherent/scripts/addBrPortSdn %s %s" % (ap, intf))
       
    def setBw(self, ap, wlan):
        """ Set bw to AP """  
        iface =  str(ap) + '-wlan' + str(wlan)
        
        value = deviceDataRate(ap, None, None)
        bw = value.rate
        
        ap.pexec("tc qdisc replace dev %s \
            root handle 2: netem rate %.2fmbit \
            latency 1ms \
            delay 0.1ms" % (iface, bw))   
        #Reordering packets    
        ap.pexec('tc qdisc add dev %s parent 2:1 pfifo limit 1000' % iface)
        
    def APfile(self, cmd, ap, wlan):
        """ run an Access Point and create the config file  """
        iface = str(ap) + '-wlan' + str(wlan)
        #print "stuff"
        #print iface
        apcommand = cmd + ("~\' > %s.conf" % iface)  
        #print apcommand
        ap.cmd(apcommand)
        #os.system(apcommand)
        # ip netns exec  ap.pid
        #print ('ip netns identify %s' % str(ap.pid))
        #print os.system('ip netns identify %s' % str(ap.pid))
        #print os.system('ip netns pids %s' % ap.name)
        #cmd = ("ip netns exec %s hostapd -B %s.conf" % (ap.pid, iface))
        #print "ls home"
        #print os.system('ls ~')
        cmd = ("hostapd -B ~/%s.conf" % (iface))
        #print cmd
        print "Starting hostapd (%s)" % ap.name
        out = ap.cmd(cmd)
        #print out
        debug(out)
        #subprocess.check_output(cmd, shell=True)