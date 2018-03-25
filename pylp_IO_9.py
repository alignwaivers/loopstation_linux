import launchpad, random, rtmidi, evdev

from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types, threading


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
        self.mode = 0
        self.states = {}

        self.cmds = [ "record", "overdub", "replace", "insert",
                  "pause","oneshot","undo", "redo"]

##    '''      #/sl/#/set s:control f:value
##                ["sync"
##              "relative_sync"]
##                #set_sync_pos '''
    
    def command(self, x, y):
        if x < 8:
            print self.cmds[x]
            try:
                slcli.send( OSCMessage("/sl/" + str(y) + "/down", Soop.cmds[x]) )
            except:
                print "Connection refused"
    
class Lpad_lights():
    def __init__(self): # for holding values of modes / color groupings
        self.thread = 1
        
        self.fg = {} #foreground
        self.bg0 = {}
        fg = self.fg
        bg0 = self.bg0
        
        #self.layouts = [fg,bg0] #add more later
        
        self.bg_mode = 1 #background select    

        for x in range(9):
            for y in range(9):
                fg[ (x , y,) ] =  [0,3]
        del fg[(8,8)]
        
        
        for items in fg: #blank background to start
            bg0[items] = 0,0


        bg1 = fg.copy()
        for items in bg1:
            bg1[items] = [random.randint(0,3), random.randint(0,3)]
            
        print bg1        
        print random.randint(0,3)

        bg2 = fg.copy()
        
        self.bg_sel = [bg0, bg1, bg2] #for multiple modles

        for r in range(4):
            for c in range(4):
                bg0[(r,c + 4)] = [r,c]

       
    def mode_switch(self, mode):
        
        newbg = self.bg_sel[mode]

        for buttons in newbg:
            print buttons[0], buttons[1] , newbg[buttons][0], newbg[buttons][1]
            
            l.light(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])

                        
            #update difference in current vs last mode



    
        

def lp_input():
    while 1:
        event = l.poll()
        note_on = [0x90, 60, 112]
        note_off = [0x80, 60, 0]

        
        if event != None:
            print 'event', event

            
            
            event = list(event)
            event[2] =int(event[2])
            event.append(event[2])
            print event[:3]

            x,y = event[0],event[1]

            note = 0
        
##            if event[2] == 1: #send to sl if its a press
##                Soop.command(event[0], event[1])


            #this should probably be a for loop
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
                l.light(event[0], event[1], 3, 3)
            elif event[2] == 0:
                midisel.send_message([0x80, note + 36, event[2]])
                l.light(event[0], event[1], 0, 0)

            try:
##                client.send( OSCMessage("/lp", event[:3]))
                #client.send( OSCMessage("/lp2", [event[0], event[1], 3, 3]))
                #print  'tryyy', [event[:2], 3, 3]
                print 'tryin'
                
            #    l.light(event[0], event[1], 3, 3)

            except:
                print ('error: connection probably refused')

            


 
def handle_error(self,request,client_address):
    print self, request, client_address ##additional details


def lp_mode(path, tags, args, source):
    if path == '/mode':

        #stopthread argument
        if args[0] == "stopthread":
            Pad.thread = 0
        
        print 'lpmode', args
        Pad.mode_switch(args)
        

def lp_callback(path, tags, args, source):
    x, y = args[:2]

    #print 'on/off', args[2]
    if args[2] == 1:
        l.light(x, y, Pad.fg[x,y][0], Pad.fg[(x,y)][1]) 
    else:
        l.light(x, y, Pad.bg0[x,y][0], Pad.bg0[(x,y)][1]) 

def lp_background(path, tags, args, source):
    ''' background colors update (of Pad.bg0 dictionary and lights immediately)'''
    
    Pad.bg0[args[0], args[1]] =  args[2:]

    #print 'args', args
    l.light(*args)

    
def server_thread():
    while Pad.thread == 1:
        server.handle_request()
        sleep(.01)
    
def pedal()

if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler("/lp", lp_callback) #for button presses (foreground)
    server.addMsgHandler("/lp2", lp_background) #for background
    server.addMsgHandler("/mode", lp_mode)
    server.addMsgHandler("/ped", pedal)
    
    server.handle_error = types.MethodType(handle_error, server)


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


    #init launchpad
    ls = launchpad.findLaunchpads()
    print ls
    try: 
        l = ls[0]
        l = launchpad.launchpad(*l)
        l.setDrumRackMode()

        l.reset()
    except IndexError:
        print "launchpad not found"

    
    Pad = Lpad_lights()
    Soop = Sl()


    for items in Pad.bg0: # display bg0
        l.light(items[0], items[1], Pad.bg0[items][0], Pad.bg0[items][1])

    #display / cycle through modes, end with bg0 (default background)
    Pad.mode_switch(1)
    sleep(.2)
    Pad.mode_switch(2)
    sleep(.2)
    Pad.mode_switch(0)
    
    #begin threads, should loop based on functions
    t = threading.Thread(name='pad inputs', target=lp_input)
    t.start()

    sleep(1)

    while 1:
        server.handle_request()
    






##    print threading.activeCount()
##
##    print t2.isAlive()

    server.close() 
