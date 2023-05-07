# constants.py file contains server and protocol specific details
from constants import SERVER_PORT, SERVER_IP, DISCONNECT_MESSAGE, HEADER,FORMAT
import socket, threading

# contains methods and definitions related to Server Process
class Server:

    # method called on creating an instance of Server
    # makes call to start which initializes the server
    def __init__(self):
        self.id = '000000'
        self.clients = []
        self.database = {}
        self.s = None
        self.start()


    # handles requests and queries from a client
    def handle_client(self,c,addr):

        # sending a thank you message to client
        c.send('Successfully connected\n'.encode(FORMAT))

        data = ""
        connected = True    # turns false when user wants to disconnect
        while connected:

            # wait for message from client and store its decoded string in data
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
                print("[MESSAGE FROM "+str(addr)+" ] "+data)
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

                # client wishes to deregister
                if data[:2] == "d:":
                    liblist = data[2:].split(',')
                    self.user_deregister(liblist[0],addr[0],addr[1])
                    c.send("Successfully deregistered".encode(FORMAT))

            # clearing data variable for next message
            data = ""


    # setup server to listen to client requests
    def start(self):
        try:

            # self.s stores the socket which receives client requests
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ("--- Socket successfully created for server ---")

            self.s.bind((SERVER_IP, SERVER_PORT))      # bind to address specified in constants.py  
            print ("--- Socket binded to %s" %(SERVER_PORT)+' ---')
 
            self.s.listen(5)        # the value states how many requests are served simultaneously   
            print ("--- Socket is listening ---")

        except socket.error as err:
            self.s = None
            print ("--- Socket creation failed with error %s" %(err)+' ---')
            exit(1)

        # start listening for clients
        while True:

            # Establish connection with client.
            c, addr = self.s.accept()    
            print ('--- Got connection from '+str(addr)+' ---')

            # Creating a new thread for each client
            thread = threading.Thread(target=self.handle_client,args=(c,addr))
            thread.start()

            # no of threads running
            print("--- Active Connections : "+str(threading.active_count()-1)+" ---\n")


    # register a user on the server
    def user_register(self,id,ip,port,data):

        # update the list of clients registered
        self.clients.append((id,ip,port))

        # update the database
        self.database[(id,ip,port)] = []
        for x in data:
            self.database[(id,ip,port)].append(x); 
        print('\n--- User registered successfully ---')
        print("Updated Database : "+str(self.database)+"\n")


    # handle a book request from client, returns the peer's address who holds the book, if present
    # else null (\0)
    def book_request(self,name):
        for x in self.database.keys():
            if name in self.database[x]:
                return str(x[0])+','+str(x[1])+","+str(x[2])
        else:
            return "\0"

    # removes the user from clients and respective books from database
    def user_deregister(self,id,ip,port):
        
        # remove client from clients list
        self.clients.remove((id,ip,port))

        # remove the client' books reference from database
        del self.database[(id,ip,port)]

        print("\n ---Client successfully deregistered--- \n")




