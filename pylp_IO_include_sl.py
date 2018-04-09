import launchpad, random, rtmidi, os

from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types, threading

import sl_indy_5


'''python script to control sooperlooper via open sound control (OSC), midi output for instruments and the launchpad '''

class SL_global():
    def __init__(self):
        self.num_loops = 1
        self.state_clr=[ [0,0], #off
                         [1,0], #waitstart
                         [3,0], #recording
                         [0,0], #waitstop
                         [0,3], #playing
                         [2,2], #overdub
                         [0,0], #multiplying
                             ]
        self.cmds = [ "record", "overdub", "replace", "insert",
                      "pause","oneshot","undo", "redo"]

        
##            '''state   ::
##             -1 = unknown,
##		0 = Off
##		1 = WaitStart
##		2 = Recording
##		3 = WaitStop
##		4 = Playing
##		5 = Overdubbing
##		6 = Multiplying
##		7 = Inserting
##		8 = Replacing
##		9 = Delay
##		10 = Muted
##		11 = Scratching
##		12 = OneShot
##		13 = Substitute
##		14 = Paused
##'''        
        
    '''      #/sl/#/set s:control f:value
                ["sync"
              "relative_sync"]
                #set_sync_pos '''
    
    def command(self, x, y):
        if x < 8:
            print y, self.cmds[x]
            try:
                cli.send( OSCMessage("/sl/" + str(y) + "/down", self.cmds[x]) )
            except:
                pass

    
class Loop(SL_global):
    def __init__(self, cli):
        SL_global.__init__(self)

        print 'initializing loop class'
        
    
        self.len = 1
        self.pos = 1
        self.state = 0
        self.pos_eigth = 0

        loop_which = "0"

        cli.send( OSCMessage("/sl/" + loop_which + "/register_auto_update", ["state", 10, "localhost:8000", '/state'] ) )
        cli.send( OSCMessage("/sl/" + loop_which  + "/register_auto_update", ["loop_pos", 10, "localhost:8000", '/sl_pos'] ) )
        cli.send( OSCMessage("/sl/" + loop_which  + "/register_auto_update", ["loop_len", 100, "localhost:8000", '/sl_len'] ) )

   

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
        
        self.layer_sel = [fg, bg, bg1, bg2]  # for different layers

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

    def alter_bg(self, x, y, r, g, layer=1):
        layer = Pad.layer_sel[layer]

        layer[x, y] = [r, g]

        l.light(x, y, r, g)


        
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
                    try:
                        looplist[y].command(x, y)
                        midisel.send_message([0x90, note, event[2]*127 ])
                    
                        Pad.lighty(x, y, 1)

                    except IndexError:
                        pass
                    
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


def gen_callback(path, tags, args, source):
    print args  

def lp_callback(path, tags, args, source):
    print 'callback', args
    
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



def sl_state(path, tags, args, source):
    print 'sl_state', args
    if path=="/state":  #without len and pos running, works 100% without latency
            state = int(args[2])
            loop = looplist[args[0]]

            loop.state = state           
            r, g = Loops.state_clr[state]
            print 'state', state, 'r ', r, 'g ', g
            
            r, g = Loops.state_clr[state][0], Loops.cmds[state][1]
            Pad.alter_bg(8, loop , r, g)
            
            #client2.send( OSCMessage("/lp2", [8,args[0], Soup.stat[state][0], Soup.stat[state][1] ] ) )
                


def sl_length(path, tags, args, source):  # only sends when theres a NEW length based on auto_register so if run this script when length is already set... issues
    pass
    print 'sl_length', args
    if args[1] == "loop_len":
        loop = args[0]
        looplist[loop].len = float(args[2])
        print looplist[loop].len 
        
        #while recording, red lights == # of seconds recorded
        sec = int(args[2])
        if looplist[loop].state == 2 and sec < 8:
            #client2.send( OSCMessage("/lp2", (sec,args[0], 2, 0) ) )
            Pad.alter_bg(sec, loop, 2, 0)           

##
def sl_pos(path, tags, args, source):
    pass
##    print 'sl_pos', args
##    #doesn't work till record is pressed after script is going
##    if path=="/sl_pos":
##        if looplist[args[0]].state != 2:
##            pos =  args[2] 
##            
##            eigth_pos = int((pos / looplist[args[0]].len) * 8)
##                
##            if looplist[args[0]].pos_eigth != eigth_pos: #dont repeat values more than once
##                
##                print args[0], eigth_pos
##                
##                looplist[args[0]].pos_eigth = eigth_pos
##                
##                #client2.send( OSCMessage("/lp2", [eigth_pos ,args[0],0,1 ] ) )
##
##                if eigth_pos > 0: #return previous position led to bg color
##                    pass
##                    #client2.send( OSCMessage("/lp2", [eigth_pos - 1,args[0],0,0] ) )
##                elif eigth_pos == 0:
##                    #client2.send( OSCMessage("/lp2", [7 ,args[0],0,0] ) )
##                    pass            


if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler("/lp", lp_callback) #for button presses (foreground)
    server.addMsgHandler("/bg", lp_background) #for background
    server.addMsgHandler("/sl", gen_callback)
    #server.addMsgHandler( "/ping", callback)    
    #server.handle_error = types.MethodType(handle_error, server)
    
    #slserver = OSCServer(("127.0.0.1", 7777))
    server.addMsgHandler("/state", sl_state)
    server.addMsgHandler("/sl_len", sl_length)
    server.addMsgHandler("/sl_pos", sl_pos) #for background
    #slserver.handle_error = types.MethodType(handle_error, server)
    

    slcli = OSCClient() #send to sooperlooper
    slcli.connect( ("localhost", 9951) ) 

    Loops = SL_global()
    
    S = Loop(slcli)
    S1 = Loop(slcli)
    S2 = Loop(slcli)
    S3 = Loop(slcli)
    
    looplist = [S, S1, S2, S3]

          

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
        l = 0

    Pad = Lpad_lights() #init
    Pad.monochrome(0, 0, 3) #fg
    Pad.monochrome(3, 1, 2) #bg2
    

    #display / cycle through modes, end with bg (default background)
    if l: #if launchpad found
        for i in range(3):
            Pad.bg_switch(3)
            Pad.bg_switch(2)
            Pad.bg_switch(0)   
            Pad.bg_switch(1)
            sleep(.3)
    #begin threads, should loop based on functions
    t = threading.Thread(name='pad inputs', target=input_thread) #switched to threading OSC as latency affectd OSC handler
    t.start()


    for i in range(2): #must do twice to determine the connection failed?
        try:
            slcli.send( OSCMessage("/ping", ["localhost:8000", '/sl'] ) )
        except:
            print "Connection refused"
            #Pad.mode == 'off'

    #register for loops being added        
    slcli.send( OSCMessage("/register", ["localhost:8000", '/sl'] ) )
    

    while 1:
        try:
            server.handle_request()
            #slserver.handle_request()
            #lp_input()

        except KeyboardInterrupt:
            Pad.thread = 0
            print "keyboard interrupted: exiting \n please reconnect launchpad before restarting"
            os._exit(1) #.... for some reason wont detect inputs after exiting, must reconnect

