import launchpad

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
        self.bg = {}
        fg = self.fg
        bg = self.bg
        

        for x in range(9):
            for y in range(9):
                fg[ (x , y,) ] =  [0,3]
        del fg[(8,8)]
        
        
        for items in fg:
            bg[items] = 0,0

        
        self.layout = [fg.copy(), fg.copy(), fg.copy()]
        print type(self.layout[0])
        
        self.layouts = [fg,bg] #add more later
        
        self.bg_mode = 1 #background select

        for r in range(4):
            for c in range(4):
                bg[(r,c + 4)] = [r,c]
        print bg

        
      



def lp_callback(path, tags, args, source):
    x, y = args[:2]

    #print 'on/off', args[2]
    if args[2] == 1:
        l.light(x, y, Pad.fg[x,y][0], Pad.fg[(x,y)][1]) 
    else:
        l.light(x, y, Pad.bg[x,y][0], Pad.bg[(x,y)][1]) 

def lp_layout2(path, tags, args, source):
    
    #print (args[0], args[1]), args[2:]
    Pad.bg[args[0], args[1]] =  args[2:]
    
    l.light(*args)


    #sleep(1)
    


    
if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler( "/lp",lp_callback) #for button presses (foreground)
    server.addMsgHandler( "/lp2",lp_layout2) #for background
    
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


    for items in Pad.bg: # display bg
        l.light(items[0], items[1], Pad.bg[items][0], Pad.bg[items][1])



    while True:
        server.handle_request()        
        
        
                
    	




server.close() 
