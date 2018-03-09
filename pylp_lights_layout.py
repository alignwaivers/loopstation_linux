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
    def __init__(self): # for holding values of
        layout = {} #foreground

        for x in range(9):
            for y in range(9):
                layout[ (x , y,) ] =  [0,3]
        del layout[(8,8)]

        print layout

        print '*' * 80
        
        layout2 = {}
        for items in layout:
            layout2[items] = 0,0

        print '*' * 80

        print layout2


        
        layout3 = layout.copy()
        layout4 = layout.copy()

        self.layout = layout   #active presses
        self.layout2 = layout2 #backgrounds for modes
        self.layout3 = layout3
        self.layout4 = layout4
        
        self.layouts = [layout, layout2, layout3, layout4]
        self.mode = 1 #background select

        for r in range(4):
            for c in range(4):
                layout2[(r,c + 4)] = [r,c]
        print layout2

        
      



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


    #sleep(1)
    


    
if __name__=="__main__":

    server = OSCServer(("127.0.0.1", 8000))
    server.addMsgHandler( "/lp",lp_callback) #for individual light
    server.addMsgHandler( "/lp2",lp_layout2) #for layout2
    
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
    #default colors hash
        Pad = Lpad()


    for items in Pad.layout2: # display layout2
        l.light(items[0], items[1], Pad.layout2[items][0], Pad.layout2[items][1])

    while True:
        server.handle_request()        
        
        
                
    	




server.close() 
