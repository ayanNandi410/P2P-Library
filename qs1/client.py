import socket, threading
from constants import SERVER_PORT, SERVER_IP, HEADER,FORMAT

class Client:

    def __init__(self,id,ip,data):
        self.id = id
        self.ip = ip
        self.dataset = data
        self.s = None
        self.peer = None
        self.running = True
        self.start()

    def start(self):

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ("---Socket successfully created for client")
        except socket.error as err:
            self.s = None
            print ("---Socket Creation failed with Error : %s" %(err))
            exit(1)

        try:
            # connect with server
            self.make_connection()

            peer_thread = threading.Thread(target=self.serve_book,args=())
            peer_thread.start()

            while True:

                print("\nOperations:\n 1. Register\n 2. Query Book\n 3. Deregister\n 4. Quit\n")
                choice = int(input("(Enter choice):"))

                if choice not in [1,2,3]:
                    if choice == 4:
                        break
                    else:
                        print("Invalid input! Try again...")
                        continue
                else:
                    if choice == 1:
                        self.register_user()
                    elif choice == 2:
                        name = input("Enter name of book : ")
                        self.query_book(name)
                    elif choice == 3:
                        self.deregister_user()
                    else:
                        print("Try again...")
                        continue


            #self.s.send("y:00002,Phantom1\n")

            self.running = False

            self.close_connection()

        except ConnectionRefusedError:
            print("[ERROR] Server not running...")
            exit(1)
        #except Exception as e:
        #   print("[ERROR] "+repr(e))
        #   exit(1)
        
    def make_connection(self):
        self.s.connect((SERVER_IP,SERVER_PORT))
        print ("[SERVER] "+self.s.recv(HEADER).decode(FORMAT))

        # start listening for book requests
        try:
            self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ("---Socket successfully created for client (Peer connection) ---")
        except socket.error as err:
            self.peer = None
            print ("---Socket Creation failed with Error : %s" %(err))
            exit(1)

    def close_connection(self):
        self.s.send("q\n".encode())
        self.s.close() 
        print ("--- Connection with Server closed ---")

    def register_user(self):
        reg_message = "r:"+str(self.id)+","+",".join(self.dataset)+"\n"
        self.s.send(reg_message.encode(FORMAT))
        print("[SERVER] "+self.s.recv(HEADER).decode(FORMAT))

    def query_book(self,name):

        # checking whether client itself has the book
        if name in self.dataset:
            print("Present in own Database\n")
            return

        # querying the server for the book
        query_message = "y:"+str(self.id)+","+name+"\n"
        self.s.send(query_message.encode(FORMAT))

        response = self.s.recv(HEADER).decode(FORMAT)
        if response[2:-1] == '\0':
            print("[SERVER] Book Not Found\n")
        else:
            print("[SERVER] "+response[2:-1])

            # query book from peer
            try:
                msgList = response[2:-1].split(",")
                sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn = sckt.connect((msgList[1],int(msgList[2])))
                msg = "s:"+name+"\n"
                sckt.send(msg.encode(FORMAT))

                response = sckt.recv(HEADER).decode(FORMAT)
                print("[PEER] "+response)

            except ConnectionRefusedError:
                print("[ERROR] Peer not listening...")
                return
            #except Exception as e:
            #   print("[ERROR] "+repr(e))
            #   return  

    def serve_book(self):
        address = self.s.getsockname()
        print(address)
        self.peer.bind(address)
        self.peer.listen(10)
        print("Listening for connections on "+str(self.id)+","+str(self.peer.getsockname()[1])+" ---")
        
        while self.running:
            c, addr = self.peer.accept()
            print(" Accepted connection from "+str(addr)+" ---")

            message = c.recv(HEADER).decode(FORMAT)

            if message[:2] == "s:":
                book_name = "Book: "+message[2:-1]
                
                # send book back
                c.send(book_name.encode(FORMAT))


    def deregister_user(self):
        pass