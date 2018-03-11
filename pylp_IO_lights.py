import launchpad, types, rtmidi

from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types


''' order of operations: pylp_21 -> lp_server(this script) -> sl



    to do:

    wait-record to blink red
    dynamic adding of loops (from launchpad)

    questions?

    time release stuff without interrupting flow ..
    hmm control flow questions, restarting loops (continue)
    and breaks
    

'''


class Sl():
    def __init__(self):

        self.cmd = [ "record", "overdub", "replace", "insert",
                  "pause","oneshot","undo", "redo"]

##    '''      #/sl/#/set s:control f:value
##                ["sync"
##              "relative_sync"]
##                #set_sync_pos '''
    
 


class Lpad():
    def __init__(self):
        self.upperlow = 16
        self.uppermid = 64

        ls = launchpad.findLaunchpads()
        
        print ls
        try:
            
            l = ls[0]
            l = launchpad.launchpad(*l)
            l.setDrumRackMode()
            l.reset()
    
        except IndexError:
            print "no launchpad found"
            l = 0
            
        finally:
            layout = {} #foreground
            self.l = l
        for x in range(9):
            for y in range(9):
                layout[ (x , y,) ] =  [0,3]
        del layout[(8,8)]
        
        layout2 = {}
        for items in layout:
            layout2[items] = 0,0
        
        layout3 = layout.copy()
        layout4 = layout.copy()

        self.layout = layout   #active presses
        self.layout2 = layout2 #backgrounds for modes
        self.layout3 = layout3
        self.layout4 = layout4
        
        self.layouts = [layout, layout2, layout3, layout4]
        self.mode = 1 #background select

        for r in range(4): #colors top right
            for c in range(4):
                layout2[(r,c + 4)] = [r,c]
        print layout2

        
        if l:
            for items in self.layout2: # display layout2
                l.light(items[0], items[1], layout2[items][0], layout2[items][1])


        
def sl_cmd(x, y):
    if x < 8:
        print Slpad.cmd[x]
        
    
def lpresses():
    event = Pad.l.poll()
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
            sl_cmd(event[0], event[1])

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

        if note < 64:
            sl_cmd(x,y)
        
        
        if note < Pad.upperlow:   #seperate to different midi ports
            midisel = midiout
        elif note < Pad.uppermid:
            midisel = midiout2
        else:
            midisel = midiout3
            
        if event[2] == 1:
            midisel.send_message([0x90, note + 36, event[2]*127 ])
        elif event[2] == 0:
            midisel.send_message([0x80, note + 36, event[2]])
        

        Pad.l.light(x, y, Pad.layout[x,y][0], Pad.layout[x,y][1])
        

def handle_error(self,request,client_address):
    print self, request, client_address ##additional details
    


def lp_callback(path, tags, args, source):
    x, y = args[:2]

    #print 'on/off', args[2]
    if args[2] == 1:
        l.light(x, y, Pad.layout[x,y][0], Pad.layout[(x,y)][1]) 
    else:
        l.light(x, y, Pad.layout2[x,y][0], Pad.layout2[(x,y)][1]) 

def lp_layout2(path, tags, args, source):
    
    #print (args[0], args[1]), args[2:]
    Pad.layout2[args[0], args[1]] =  args[2:]
    
    l.light(*args) 


    
if __name__=="__main__":
    
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

    
    slcli = OSCClient() #send to sooperlooper
    slcli.connect( ("localhost", 9951) )

    ostagec = OSCClient() #send to
    ostagec.connect( ("localhost", 7777) )

    ostagesrv = OSCServer( ("127.0.0.1", 8080) )
    ostagesrv.addDefaultHandlers()
    
    

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler( "/lp",lp_callback) #for individual light
    server.addMsgHandler( "/lp2",lp_layout2) #for layout2
    
    server.handle_error = types.MethodType(handle_error, server)


    #init launchpad
    Pad = Lpad()
    #init slcommands
    Slpad = Sl()
    
    while True:
        server.handle_request()
        if Pad.l:
           lpresses()
           pass
        
server.close() 
