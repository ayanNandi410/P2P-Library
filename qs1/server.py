from constants import SERVER_PORT, SERVER_IP, DISCONNECT_MESSAGE, HEADER,FORMAT
import socket, threading


class Server:

    def __init__(self):
        self.id = '000000'
        self.clients = []
        self.database = {}
        self.s = None
        self.start()

    def handle_client(self,c,addr):

        # send a thank you message to the client. encoding to send byte type.
        c.send('Successfully connected\n'.encode(FORMAT))

        data = ""
        connected = True
        while connected:

            data = c.recv(HEADER).decode(FORMAT)

            if len(data) == 0 or data[-1] != '\n':
                continue

            if data == DISCONNECT_MESSAGE:
                print("--- Closing connection ---")
                c.close()
                connected = False
            # client's connection remains on
            else:
                # Printing message from client
                print("[MESSAGE] "+data)
                data = data[:-1]

                # client wishes to register
                if data[:2] == "r:":
                    liblist = data[2:].split(',')
                    self.user_register(liblist[0],addr[0],addr[1],liblist[1:])
                    c.send("Successfully registered".encode(FORMAT))

                # client is requesting for a book
                # Server replies with the granting member's address
                if data[:2] == "y:":
                    query = data[2:].split(',')
                    id, name = query[0], query[1]
                    result = self.book_request(name)
                    response = "p:"+result+'\n'
                    c.send(response.encode(FORMAT))

            # clearing data variable for next message
            data = ""

    def start(self):

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ("--- Socket successfully created for server ---")

            self.s.bind((SERVER_IP, SERVER_PORT))        
            print ("--- Socket binded to %s" %(SERVER_PORT)+' ---')
 
            self.s.listen(5)    
            print ("--- Socket is listening ---")

        except socket.error as err:
            self.s = None
            print ("--- Socket creation failed with error %s" %(err)+' ---')
            exit(1)

        while True:

            # Establish connection with client.
            c, addr = self.s.accept()    
            print ('--- Got connection from '+str(addr)+' ---')

            # Creating a new thread for each client
            thread = threading.Thread(target=self.handle_client,args=(c,addr))
            thread.start()
            print("--- Active Connections : "+str(threading.active_count()-1)+" ---\n")



    def user_register(self,id,ip,port,data):
        self.clients.append((id,ip,port))
        self.database[(id,ip,port)] = []
        for x in data:
            self.database[(id,ip,port)].append(x); 
        print('\n--- User registered successfully ---')
        print("Updated Database : "+str(self.database)+"\n")

    def book_request(self,name):
        for x in self.database.keys():
            if name in self.database[x]:
                return str(x[0])+','+str(x[1])+","+str(x[2])
        else:
            return "\0"


    def user_deregister(self,id,ip):
        pass


