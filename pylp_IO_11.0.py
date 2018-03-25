import launchpad, random, rtmidi, os

from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types, threading


'''python script to control sooperlooper via open sound control (OSC), midi output for instruments and the launchpad '''


class Sl():                                 
    def __init__(self):
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
        self.highbound = 67
        self.lowbound = 16

        self.thread = 1



        self.fg = {} #foreground
        self.bg = {} #background
        self.pressed = {}
        fg = self.fg
        bg = self.bg
        pressed = self.pressed

        
        #self.layouts = [fg,bg0] #add more later

        for x in range(9):
            for y in range(9):
                fg[ (x , y,) ] =  [0,3]
        del fg[(8,8)]
        
        
        for items in fg: #blank background to start
            bg[items] = 0,0


        bg1 = fg.copy()
        bg2 = fg.copy()


        for items in bg1:
            bg1[items] = [random.randint(0,3), random.randint(0,3)]


        
        self.bg_sel = [bg, bg1, bg2] #for multiple modes
        self.mode = 0
        for r in range(4):
            for c in range(4):
                bg[(r,c + 4)] = [r,c]

       
    def mode_switch(self, mode):
        #switch displays  ____could be done more dynamically w/ less memory waste - difference bw dicts?
        self.mode =  mode
        #l.LedCtrlString(str(mode), 0, 3, -1)

        newbg = self.bg_sel[mode]
        for buttons in newbg:
            print buttons[0], buttons[1] , newbg[buttons][0], newbg[buttons][1]
            
            l.light(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])


    def lighty(self, x, y, vel):
        '''light up pad'''
        #depending on Pad.lmode
        red = Pad.fg[(x, y,)][0]
        green = Pad.fg[(x, y,)][1]
        if vel: #button press
            l.light(x, y, red, green)
        elif vel == 0:
            l.light(x, y, Pad.bg[(x, y,)][0], Pad.bg[(x, y,)][0])

def lp_input():
    '''get input from launchpad'''
    while Pad.thread == 1:
            event = l.poll()

            if event != None:
                print 'event', event
                event = list(event)
                event[2] =int(event[2])
                event.append(event[2])
                x,y = event[0],event[1]

                note = 0
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

                if note < Pad.lowbound:   #seperate to different midi ports
                    midisel = midiout
                elif note < Pad.highbound:
                    midisel = midiout2
                else:
                    midisel = midiout3

                if event[2] == 1:
                    midisel.send_message([0x90, note + 36, event[2]*127 ])
                    #l.light(event[0], event[1], 3, 3)
                    Pad.lighty(event[0], event[1], 1)
                elif event[2] == 0:
                    midisel.send_message([0x80, note + 36, event[2]])
                    #l.light(event[0], event[1], 0, 0)
                    Pad.lighty(event[0], event[1], 0)


 
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
        l.light(x, y, Pad.bg[x,y][0], Pad.bg[(x,y)][1])

def lp_background(path, tags, args, source):
    ''' background colors update (of Pad.bg dictionary and lights immediately)'''
    Pad.bg[args[0], args[1]] =  args[2:]

    #print 'args', args
    l.light(*args)

    
def server_thread():
    while Pad.thread == 1:
        server.handle_request()
        sleep(.01)
    
def pedal():
    pass

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
    midi_masha = rtmidi.MidiOut(name = "RtMidi Masha")
    available_ports = midiout.get_ports()
    
    if available_ports:
        midiout.open_port(0)
        midiout2.open_port(0)
        midiout3.open_port(0)
        midi_masha.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")


    #init launchpad
    ls = launchpad.findLaunchpads()
    print ls
    try:
        print "trying to launchpad"
        l = ls[0]
        l = launchpad.launchpad(*l)
        l.setDrumRackMode()

        l.reset()
    except IndexError:
        print "launchpad not found"

    
    Pad = Lpad_lights()
    Soop = Sl()




    for items in Pad.bg: # display bg
        l.light(items[0], items[1], Pad.bg[items][0], Pad.bg[items][1])

    #display / cycle through modes, end with bg (default background)
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
        try:
            server.handle_request()
        except KeyboardInterrupt:
            Pad.thread = 0
            print "keyboard interrupted: exiting \n please reconnect launchpad before restarting"
            os._exit(1) #.... for some reason wont detect inputs after exiting though






##    print threading.activeCount()
##
##    print t2.isAlive()

    server.close() 
