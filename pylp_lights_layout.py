import launchpad, random

from OSC import OSCServer,OSCClient
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



 
def handle_error(self,request,client_address):
    print self, request, client_address ##additional details
    


class Lpad():
    def __init__(self): # for holding values of modes / color groupings
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
        print
        newbg = self.bg_sel[mode]

        for buttons in newbg:
            print buttons[0], buttons[1] , newbg[buttons][0], newbg[buttons][1]
            
            l.light(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])

                        
            #update difference in current vs last mode
      

def lp_mode(path, tags, args, source):
    if path == '/mode'
        print args
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
    #only need to use 
    Pad.bg0[args[0], args[1]] =  args[2:]

    print 'args', args
    l.light(*args)


    #sleep(1)
    


    
if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler("/lp", lp_callback) #for button presses (foreground)
    server.addMsgHandler("/lp2", lp_background) #for background
    server.addMsgHandler("/mode", lp_mode)

    
    server.handle_error = types.MethodType(handle_error, server)





    #init launchpad
    ls = launchpad.findLaunchpads()
    print ls
    try: 
        l = ls[0]
        l = launchpad.launchpad(*l)
        l.setDrumRackMode()

        l.reset()
    finally:
    
        Pad = Lpad()


    for items in Pad.bg0: # display bg0
        l.light(items[0], items[1], Pad.bg0[items][0], Pad.bg0[items][1])


    Pad.mode_switch(1)

    sleep(.5)

    Pad.mode_switch(2)

    sleep(.5)

    Pad.mode_switch(0)
    
    while True:
        server.handle_request()


        
        
                
    	




server.close() 
