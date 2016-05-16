"""

author: Ramon Fontes (ramonrf@dca.fee.unicamp.br)
        ramonfontes.com

"""

import subprocess

class emulationEnvironment ( object ):
    
    propagation_Model = ''
    wpa_supplicantIsRunning = False
    associationControlMethod = False
    isWiFi = False
    isCode = False
    continue_ = True
    DRAW = False
    printCon = True
    meshRouting = ''
    physicalWlan = []
    apList = []
    staList = []
    totalPhy = []
    wifiRadios = 0 
    loss = 0
    meshssidID = 0
    
    @classmethod
    def numberOfAssociatedStations( self, ap ):
        "Number of Associated Stations"
        cmd = 'iw dev %s-wlan0 station dump | grep Sta | grep -c ^' % ap     
        """
        proc = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE,shell=True)   
        (out, err) = proc.communicate()
        """
        out = ap.cmd(cmd)
        output = out.rstrip('\n')
        ap.nAssociatedStations = int(output)
        #print "nAssociatedStations: %s" % output
        

    
    @classmethod
    def getPhy(self):
        """ Get phy """ 
        phy = subprocess.check_output("find /sys/kernel/debug/ieee80211 -name hwsim | cut -d/ -f 6 | sort", 
                                                             shell=True).split("\n")
        phy.pop()
        return phy
    
    