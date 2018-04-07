from OSC import OSCServer,OSCClient, OSCMessage
from time import sleep
import types


class SL_global(object):
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
        
    
        self.len = 1
        self.pos = 1
        self.state = 0
        self.pos_eigth = 0

        loop_which = "0"

        cli.send( OSCMessage("/sl/" + loop_which + "/register_auto_update", ["state", 10, "localhost:7777", '/state'] ) )
        cli.send( OSCMessage("/sl/" + loop_which  + "/register_auto_update", ["loop_pos", 10, "localhost:7777", '/sl_pos'] ) )
        cli.send( OSCMessage("/sl/" + loop_which  + "/register_auto_update", ["loop_len", 100, "localhost:7777", '/sl_len'] ) )
    



                
def sl_callback(path, tags, args, source):
    #if path=="/sl":
        print args
        Soup.num_loops = args[2]
        
           





if __name__=="__main__":
    server = OSCServer(("127.0.0.1", 7777))
    server.addMsgHandler( "/sl",sl_callback)
    server.addMsgHandler( "/sl_len",sl_length)
    server.addMsgHandler( "/state",sl_state)
    server.addMsgHandler( "/sl_pos", sl_pos)


    client = OSCClient()
    client.connect( ("localhost", 9951) ) #soooperlooper default port

    client2 = OSCClient()
    client2.connect( ("localhost", 8000) )

    client.send( OSCMessage("/ping", ["localhost:7777", '/sl'] ) )
  
    
    

    print looplist[0], looplist[0].len, looplist[0].pos
    print looplist[1], looplist[1].len, looplist[0].pos


    print '*' * 80
    print 'num of loops', Soup.num_loops

    client.send( OSCMessage("/ping", ["localhost:7777", '/sl'] ) )
    
    for i in range(8):     
            #client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["loop_pos", 10, "localhost:7777", '/sl_pos'] ) )
            client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["state", 10, "localhost:7777", '/state'] ) )
            #client.send( OSCMessage("/sl/" + str(i) + "/register_auto_update", ["loop_len", 100, "localhost:7777", '/sl_len'] ) )

    client.send( OSCMessage("/register", ["localhost:7777", '/sl'] ) )
        #gotta somehow ping every once in awhile or after initial reg to make sure all loops are accounted for

    client2.send( OSCMessage("/mode", (1) ) )
            
    while True:
        
            server.handle_request()

            #sleep(.1)
            #client.send( OSCMessage("/sl/0/ ", ["loop_len", 100, "localhost:7777", '/sl_len'] ) )
            #set_sync_pos
    
