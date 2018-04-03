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

    '''      #/sl/#/set s:control f:value
                ["sync"
              "relative_sync"]
                #set_sync_pos '''
    
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
        self.highbound = 67
        self.lowbound = 16
        self.mode = 0


        self.fg = {} #background
        fg = self.fg
        for x in range(9):
            for y in range(9):
                fg[ (x , y,) ] =  [0,3]
        del fg[(8,8)]
        
        self.bg = self.fg.copy() #foreground
        self.bg1 = fg.copy()
        self.bg2 = fg.copy()
        
        
        
        bg = self.bg
        bg1 = self.bg1
        bg2 = self.bg2
        
        self.layer_sel = [fg, bg, bg1, bg2]  # for multiple modes

        self.pressed = {}
        pressed = self.pressed
        
        
        for items in bg1:
            self.bg1[items] = [random.randint(0,3), random.randint(0,3)]


        for r in range(4):
            print r
            #r = -1 * r + 3
            print '-', r
            for c in range(4):
                bg[(r,c)] = [-r + 3, -c + 3]
                bg[(r + 4,c)] = [r, -c + 3]
                bg[(r,c + 4)] = [-r + 3, c]
                bg[(r+ 4,c + 4)] = [r, c]
                
                

    def monochrome(self, layer, red, green): # to make layers one color
        print layer
        layer = Pad.layer_sel[layer]
        
        for i in layer:
            layer[i] = [red, green]
        

    def mode_switch(self, mode):
        '''switch mode''' 
        
        Pad.mode = mode
        newbg = self.layer_sel[mode]
        print 'mode_switch', mode
        for buttons in newbg:
            l.light(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])
        

    def lighty(self, x, y, vel):
        '''light up individual button presses'''
        #depending on Pad.lmode, presses will light different colors and do different things
        layer = Pad.layer_sel[Pad.mode]

        red = -layer[(x, y)][0] + 3 # invert foreground color from background colors
        green = -layer[(x, y)][1] + 3

        bg = Pad.layer_sel[Pad.mode]

        if vel: #button press
            l.light(x, y, red, green)
        elif vel == 0:
            l.light(x, y, bg[(x, y,)][0], bg[(x, y,)][1])

def lp_input():
    '''get input from launchpad'''
    while Pad.thread == 1:
            event = l.poll()

            if event != None:
                event = list(event)
                event[2] =int(event[2])
                event.append(event[2])
                x,y = event[0],event[1]
                
                note = 0

            
                
                #this should probably be a list comprehension
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

                note = 0
                
                print note

                

                if note < Pad.lowbound:   #seperate to different midi ports
                    midisel = midiout
                elif note < Pad.highbound:
                    midisel = midiout2
                else:
                    midisel = midiout3

                if event[2] == 1:
                    #todo - if SL enabled in mode
                    Soop.command(x, y)                    
                    midisel.send_message([0x90, note, event[2]*127 ])
                    Pad.lighty(event[0], event[1], 1)

                    if (x,y) not in Pad.pressed:
                        Pad.pressed[x, y] = 1

                    #print Pad.pressed
                        
                elif event[2] == 0:
                    midisel.send_message([0x80, note, event[2]])                    
                    Pad.lighty(event[0], event[1], 0)

                    
                    
                    if (x,y) in Pad.pressed:
                        del Pad.pressed[x, y]

                

 
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
    bg = Pad.layer_sel[Pad.mode] 
    bg[args[0], args[1]] =  args[2:]

    if args[3] == 1:
        print 'args', args
    l.light(*args)

    
def server_thread():
    while Pad.thread == 1:
        server.handle_request()

def callback(path, tags, args, source):
    print 'callllllllback',  args

def input_thread():
    while Pad.thread == 1:
        lp_input()
        
    
def pedal():
    pass

if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler("/lp", lp_callback) #for button presses (foreground)
    server.addMsgHandler("/lp2", lp_background) #for background
    server.addMsgHandler("/mode", lp_mode)
    server.addMsgHandler( "/reg", callback)
    server.addMsgHandler( "/ping", callback)
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


    Soop = Sl()

    Pad = Lpad_lights()
    Pad.monochrome(0, 0, 3) #fg
    Pad.monochrome(3, 1, 2)

    sleep(.5)

    #display / cycle through modes, end with bg (default background)
    for i in range(3):
        Pad.mode_switch(3)
        Pad.mode_switch(2)
        Pad.mode_switch(0)   
        Pad.mode_switch(1)
        sleep(.3)
    #begin threads, should loop based on functions
    t = threading.Thread(name='pad inputs', target=input_thread) #switched to threading OSC as latency affectd OSC handler
    t.start()

    sleep(1)

    while 1:
        try:
            server.handle_request()
            #lp_input()
            
        except KeyboardInterrupt:
            Pad.thread = 0
            print "keyboard interrupted: exiting \n please reconnect launchpad before restarting"
            os._exit(1) #.... for some reason wont detect inputs after exiting, must reconnect


