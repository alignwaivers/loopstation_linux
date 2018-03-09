
import launchpad, rtmidi
from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types


class Pad():
    def __init__(self):
        self.mode = 0
        self.states = {}

        self.cmd = [ "record", "overdub", "replace", "insert",
                  "pause","oneshot","undo", "redo"]

##    '''      #/sl/#/set s:control f:value
##                ["sync"
##              "relative_sync"]
##                #set_sync_pos '''
    
def sl(x, y):
    if x < 8:
        print pad.cmd[x]
        slcli.send( OSCMessage("/sl/" + str(y) + "/down", pad.cmd[x]) )
    
    
        
        

def lpresses():
    event = l.poll()
    note_on = [0x90, 60, 112]
    note_off = [0x80, 60, 0]

    if event != None:

        
        
        event = list(event)
        event[2] =int(event[2])
        event.append(event[2])
        print event[:3]

        x,y = event[0],event[1]

        note = 0
    
        if event[2] == 1: #send to sl if its a press
            sl(event[0], event[1])


        
        if x == 8:
            note = y + 72
        
        elif y == 0:
            note = x
        elif y == 1:
            note = x + 8  
        elif y == 2:
            note = x + 16
        elif y == 3:
            note = x + 24
        elif y == 4:
            note = x + 32
        elif y == 5:
            note = x + 40
        elif y == 6:
            note = x + 48
        elif y == 7:
            note = x + 56 #top row of grid
        elif y == 8:
            note = x + 64 #top row (controls)
                
        print note

        if note < 16:   #seperate to different midi ports
            midisel = midiout
        elif note < 64:
            midisel = midiout2
        else:
            midisel = midiout3
            
        if event[2] == 1:
            midisel.send_message([0x90, note + 36, event[2]*127 ])
        elif event[2] == 0:
            midisel.send_message([0x80, note + 36, event[2]])
        

        try:
            client.send( OSCMessage("/lp", event[:3]))

        except:
            print ('error: connection probably refused')




    
if __name__=="__main__":
    #OSC
    client = OSCClient() #send to python script
    client.connect( ("localhost", 8000) )

    slcli = OSCClient() #send to sooperlooper
    slcli.connect( ("localhost", 9951) ) 

    
    #initialize midi outputs
    midiout = rtmidi.MidiOut(name = "RtMidi Low: drums")
    midiout2 = rtmidi.MidiOut(name = "RtMidi Middle: inst")
    midiout3 = rtmidi.MidiOut(name = "RtMidi High: controls")

    available_ports = midiout.get_ports()
    
    if available_ports:
        midiout.open_port(0)
        midiout2.open_port(0)
        midiout3.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    #initialize launchpad
    ls = launchpad.findLaunchpads()
    print ls
    l = ls[0]
    l = launchpad.launchpad(*l)
    l.setDrumRackMode()

    l.reset()  #

    #init pad class
    pad = Pad()

    while True:
        
        lpresses()
        
    	
