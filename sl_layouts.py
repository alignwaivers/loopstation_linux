from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types

#currently loops must be initialized BEFORE 



def handle_error(self,request,client_address):
    print self, request, client_address ##additional details




class Loop():
    def __init__(self):
        self.len = 1
        
        self.pos = 1
        
        self.state = 0

        self.pos_eigth = 0

        

class SL_global():
    def __init__(self):
        self.num_loops = 1
        self.stat =[ [0,0], #off
                     [1,0], #waitstart
                     [3,0], #recording
                     [0,0], #waitstop
                     [0,3], #playing
                     [2,2], #overdub
                     [0,0], #multiplying
                     [0,0],
                     [0,0],
                     [0,0],
                     [0,0],
                     [0,0] ]
        

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

    



def sl_state(path, tags, args, source):
    if path=="/state":  #without len and pos running, works 100% without latency
            state = int(args[2])
            
            looplist[args[0]].state = state
            
            client2.send( OSCMessage("/lp2", [8,args[0], Soup.stat[state][0], Soup.stat[state][1] ] ) )
            


def sl_length(path, tags, args, source):  # only sends when theres a NEW length so if run this script when length is already set... issues
    if args[1] == "loop_len":
        print 'len', args[2]
        looplist[args[0]].len = float(args[2])


def sl_pos(path, tags, args, source):
    if path=="/sl_pos":
        if looplist[args[0]].state != 2:
            pos =  args[2] 
            
            eigth_pos = int((pos / looplist[args[0]].len) * 8)
            
           
            

            if looplist[args[0]].pos_eigth != eigth_pos:
                #print args[0], eigth_pos
                print eigth_pos, looplist[args[0]].pos_eigth
                
                looplist[args[0]].pos_eigth = eigth_pos
                
                client2.send( OSCMessage("/lp2", [eigth_pos ,args[0],0,1 ] ) )
                if eigth_pos > 0:
                    client2.send( OSCMessage("/lp2", [eigth_pos - 1,args[0],0,0] ) )
                elif eigth_pos == 0:
                    client2.send( OSCMessage("/lp2", [7 ,args[0],0,0] ) )
            
            elif looplist[args[0]].state == 2:
                for i in range(8):
                    client2.send( OSCMessage("/lp2", [i,args[0],2,0] ) )
                        
            
            
def sl_callback(path, tags, args, source):
    #if path=="/sl":
        #print args
        Soup.num_loops = args[2]
           





if __name__=="__main__":
    server = OSCServer(("127.0.0.1", 7777))
    server.addMsgHandler( "/sl",sl_callback)
    server.addMsgHandler( "/sl_len",sl_length)
    server.addMsgHandler( "/state",sl_state)
    server.addMsgHandler( "/sl_pos", sl_pos)
    server.handle_error = types.MethodType(handle_error, server)

    client = OSCClient()
    client.connect( ("localhost", 9951) ) #soooperlooper default port

    client2 = OSCClient()
    client2.connect( ("localhost", 8000) )

    client.send( OSCMessage("/ping", ["localhost:7777", '/sl'] ) )

    Soup = SL_global()

    
    L0 = Loop()    #this should probably be done more dynamically but....
    L1 = Loop()
    L2 = Loop()
    L3 = Loop()
    L4 = Loop()
    L5 = Loop()
    L6 = Loop()
    L7 = Loop()
    
    
    looplist = [L0, L1, L2, L3, L4, L5, L6, L7]

    print looplist
    print looplist[0].len, looplist[0].pos
    print looplist[1].len, looplist[0].pos



    print '*' * 80
    print 'num of loops', Soup.num_loops
    
    for i in range(8):     
            client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["loop_pos", 10, "localhost:7777", '/sl_pos'] ) )
            client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["state", 10, "localhost:7777", '/state'] ) )
            client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["loop_len", 100, "localhost:7777", '/sl_len'] ) )


            
    while True:
        
            server.handle_request()

            #sleep(.1)
            #client.send( OSCMessage("/sl/0/ ", ["loop_len", 100, "localhost:7777", '/sl_len'] ) )
            #set_sync_pos
    
