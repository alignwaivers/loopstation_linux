import launchpad, random, rtmidi, os

from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types, threading

import sl_indy_4


'''python script to control sooperlooper via open sound control (OSC), midi output for instruments and the launchpad '''



class Lpad_lights():
    def __init__(self): # for holding values of modes / color groupings
        self.thread = 1
        self.highbound = 67
        self.lowbound = 16
        self.mode = 0


        self.fg = {} #foreground
        fg = self.fg
        for x in range(9):
            for y in range(9):
                fg[ (x , y,) ] =  [0,3]
        del fg[(8,8)]
        
        self.bg = self.fg.copy() #background
        self.bg1 = fg.copy()
        self.bg2 = fg.copy()
        
        
        
        bg = self.bg
        bg1 = self.bg1
        bg2 = self.bg2
        
        self.layer_sel = [fg, bg, bg1, bg2]  # for multiple modes

        self.pressed = {} #for tracking currently pressed buttons
        pressed = self.pressed
        
        
        for items in bg1: #random background
            self.bg1[items] = [random.randint(0,3), random.randint(0,3)]


        for r in range(4): #colorful, ordered background
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
        
 
    def bg_switch(self, mode):
        '''switch mode''' 
        newbg = self.layer_sel[mode]
        print 'bg_switch', mode
        for buttons in newbg:
            l.light(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])
        

    def lighty(self, x, y, vel, inv=1):
        '''light up individual button presses'''
        #depending on Pad.lmode, presses will light different colors and do different things
        if Pad.mode == 0 and inv == 1:
               #layer_sel[Pad.mode]
            bg = Pad.bg

            red = -bg[(x, y)][0] + 3 # invert foreground color from background colors
            green = - bg[(x, y)][1] + 3      

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
            
                note = 8 * y + x

                midis = [midi_low, midi_mid, midi_high, midi_masha]

                if note < Pad.lowbound:   #seperate to different midi ports
                    midisel = midis[0]
                elif note < Pad.highbound:
                    midisel = midis[1]
                else:
                    midisel = midis[2]

                if event[2] == 1: #note on
                    #todo - if SL enabled in mode
                    '''Soop.command(x, y) refactor '''                    
                    midisel.send_message([0x90, note, event[2]*127 ])
                    
                    Pad.lighty(x, y, 1)
                        
                    if (x,y) not in Pad.pressed:
                        Pad.pressed[x, y] = 1

                    #print Pad.pressed
                        
                elif event[2] == 0: #note off
                    midisel.send_message([0x80, note, event[2]])                    
                    Pad.lighty(x, y, 0)
                    
                    if (x,y) in Pad.pressed:
                        del Pad.pressed[x, y]

                

 
def handle_error(self,request,client_address):
    print self, request, client_address ##additional details


  

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

def input_thread():
    while Pad.thread == 1:
        lp_input()

def sl_osc():
  pass  
        
if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler("/lp", lp_callback) #for button presses (foreground)
    server.addMsgHandler("/lp2", lp_background) #for background
    #server.addMsgHandler( "/ping", callback)
    
    
    server.handle_error = types.MethodType(handle_error, server)


    slcli = OSCClient() #send to sooperlooper
    slcli.connect( ("localhost", 9951) ) 

    Soop = sl_indy_4.Loop()
    Soop.command(2, 3)
    command(2,3)

    #initialize midi outputs
    midi_low = rtmidi.MidiOut(name = "RtMidi Low:")
    midi_mid = rtmidi.MidiOut(name = "RtMidi Middle:")
    midi_high = rtmidi.MidiOut(name = "RtMidi High:")
    midi_masha = rtmidi.MidiOut(name = "RtMidi Masha")

    
    available_ports = midi_low.get_ports()
    
    if available_ports:
        midi_low.open_port(0)
        midi_mid.open_port(0)
        midi_high.open_port(0)
        midi_masha.open_port(0)


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

    Pad = Lpad_lights() #init
    Pad.monochrome(0, 0, 3) #fg
    Pad.monochrome(3, 1, 2) #bg2
    

    #display / cycle through modes, end with bg (default background)
    for i in range(3):
        Pad.bg_switch(3)
        Pad.bg_switch(2)
        Pad.bg_switch(0)   
        Pad.bg_switch(1)
        sleep(.3)
    #begin threads, should loop based on functions
    t = threading.Thread(name='pad inputs', target=input_thread) #switched to threading OSC as latency affectd OSC handler
    t.start()

    
    Soop = sl_indy_4.Loop(slcli)
    Soop.command(2, 3)
    command(2,3)

    for i in range(2): #must do twice to determine the connection failed?
        try:
            slcli.send( OSCMessage("/ping", ["localhost:8000", '/sl'] ) )
        except:
            print "Connection refused"
            #Pad.mode == 'off'

    #register for loops being added        
    slicli.send( OSCMessage("/register", ["localhost:8000", '/sl'] ) )
    

    while 1:
        try:
            server.handle_request()
            #lp_input()
            
        except KeyboardInterrupt:
            Pad.thread = 0
            print "keyboard interrupted: exiting \n please reconnect launchpad before restarting"
            os._exit(1) #.... for some reason wont detect inputs after exiting, must reconnect


