import socket
import threading
import json
import select
import argparse
from Variables import States, Client_info
import pickle
import signal
import sys
global thread_list
thread_list = []
def end(signum, frame):
	print('Bye~', flush=True)
	exit(0)
signal.signal(signal.SIGINT, end)
signal.signal(signal.SIGTERM, end)
#TODO: client database lock, client list lock

'''
class Client_info():
    def __init__(self, connect, host, port):
        self.connect = connect
        self.host = host
        self.port = port
        self.username = ""
        self.password  = ""
        self.state = States.initial
'''
class thread_accept_client(threading.Thread):
    global client_list
    global client_database
    global thread_list
    def __init__(self, listen_socket, client_list): 
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stoping Thread
        self.socket = listen_socket
        
        self.read_list = [listen_socket]

    def run(self):
       
        print(u'waiting for connect...',flush=True)
        while not self._stop_event.is_set():
            readable, writable, errored = select.select(self.read_list, [], [])
            for s in readable:
                if s is self.socket:
                     #Todo: client info maintain
                    connect, (host, port) = self.socket.accept()
                    print(u'the client %s:%s has connected.' % (host, port))
                    raw_data = connect.recv(1024)
                    data = raw_data.decode('utf-8')
                    print("Second connetion:", data, flush=True)

                    if(data == "New"):
                        new_client_info = Client_info(connect, host, port)
                        client_list.append(new_client_info)
                        #send_data = States.initial +  ":" + "Welcome"
                        #send_raw_data = send_data.encode("utf-8")
                        #connect.sendall(send_raw_data)
                        running = thread_running_client(new_client_info)
                        running.setDaemon(True)
                        running.start()
                        thread_list.append(running)
                    else:
                        flag = 0
                        for idx, info in enumerate(client_list):
                            if(data == info.username):
                                client_list[idx].sound_socket = connect
                                flag = 1
                                continue
                        if(flag == 0):
                            print(data,":Not found. This shouldn't happen.")


                    
                    
                '''
                else:  

                    recv_data = s.recv(1024)
                
                    print(recv_data,flush=True)
                    recv_data = recv_data.decode('utf-8').split(',')
                    #recv_data[1] = recv_data[1].replace("\n","")
                    print(self.database[recv_data[0]],'456',flush=True)
                    
                    if self.database[recv_data[0]] == recv_data[1]: #Check if user is valid
                        self.list.append({"host":host,
                                          "port":port,
                                          "usrname":recv_data[0],
                                          "passwd":recv_data[1],
                                          "Socket":connect
                                         })
                        connect.sendall(b'ACK')
                    else:
                        connect.sendall(b'NEG')
                '''
    def stop(self):
        self._stop_event.set()
        sys.exit()

class thread_running_client(threading.Thread):
    global mic_lock
    global client_list
    global client_database

    def __init__(self, client_info):
        threading.Thread.__init__(self)
        self.info = client_info
        self._stop_event = threading.Event() #For Stoping Thread
        self.read_list = [client_info.connect]
        self.info.connect.setblocking(True)
    def run(self):
        print("Connection Start", flush=True)
        while not self._stop_event.is_set():
            self.readable, self.writable, self.errored = select.select(self.read_list, [], [])
            # print(self.readable, flush=True)
            if self.info.connect in self.readable:
                raw_data = self.info.connect.recv(4096)
                #data = raw_data.decode('utf-8')
                data = pickle.loads(raw_data)
                print("Receive data", data)
                #print(self.info.state)
                if self.info.state == States.initial:
                    if data == States.sign_up:
                        self.info.state = States.sign_up
                        send_data = self.info.state + ":" + "Ent"
                    elif data == States.login:
                        self.info.state = States.login
                        send_data = self.info.state + ":" + "Ent"
                    elif data == "quit":
                        self.info.connect.close()
                        client_list.remove(self.info)
                        self._stop_event.set()
                        return
                    else:
                        #send_data = self.info.state + ":" + "NoImpl"
                        self.info.connect.close()
                        client_list.remove(self.info)
                        self._stop_event.set()
                        #print("not implement")
                        return

                    send_raw_data = pickle.dumps(send_data)
                    #send_raw_data = send_data.encode("utf-8")
                    self.info.connect.sendall(send_raw_data)
                        
                elif self.info.state == States.login :
                    usr,pwd = data.split(",")
                    print( usr, pwd)
                    if usr not in client_database or client_database[usr] != pwd:
                        send_data = self.info.state + ":" + "Wrong"
                        self.info.state = States.initial
                    else:
                        self.info.state = States.waiting_for_talk
                        send_data = self.info.state + ":" + "Ent"
                        self.info.username = usr
                        self.info.password = pwd

                    send_raw_data = pickle.dumps(send_data)
                    #send_raw_data = send_data.encode("utf-8")
                    self.info.connect.sendall(send_raw_data)


                elif self.info.state == States.sign_up:
                    usr, pwd = data.split(",")
                    print( usr, pwd)
                    if usr in client_database:
                        self.info.state = States.initial
                        send_data = self.info.state + ":" + "Rej"
                    else:
                        self.info.state = States.initial
                        send_data = self.info.state + ":" + "Ent"
                        self.info.username = usr
                        self.info.password = pwd
                        client_database[usr] = pwd
                        with open('db.json', 'w', encoding='utf-8') as f: #Save New Database
                            json.dump(client_database,f)
                            for x in client_database:
                                print(x, client_database)  
                    
                    send_raw_data = pickle.dumps(send_data)
                    #send_raw_data = send_data.encode("utf-8")
                    self.info.connect.sendall(send_raw_data)

                elif self.info.state == States.waiting_for_talk:
                    #print(data)
                    if data == "Req":
                        #print(123)
                        if mic_lock.acquire(blocking=False):
                            self.info.state = States.talking
                            send_data =  self.info.state + ":" + "Mic_ACK"
                        else:
                            send_data =  self.info.state + ":" + "Mic_REJ"
                    elif data == "quit":
                        self.info.state = States.initial
                        send_data = self.info.state + ":" + "Ent"
                    else:
                        self.info.connect.close()
                        client_list.remove(self.info)
                        self._stop_event.set()
                        print("Client abnormal disconect.")
                        return
                    send_raw_data = pickle.dumps(send_data) 
                    #send_raw_data = send_data.encode("utf-8")
                    self.info.connect.sendall(send_raw_data)

                elif self.info.state == States.talking:
                    if data == "quit":
                        self.info.state = States.waiting_for_talk
                        send_data = self.info.state + ":" + "Ent"
                        send_raw_data = pickle.dumps(send_data)
                        #send_raw_data = send_data.encode("utf-8")
                        self.info.connect.sendall(send_raw_data)
                        mic_lock.release()
                    else:
                        print('receive sound!!!', flush=True)
                        send_data = "start"
                        send_raw_data = pickle.dumps(send_data)
                        self.info.connect.sendall(send_raw_data)
                        self.readable, self.writable, self.errored = select.select(self.read_list, [], [])
                        while self.info.connect not in self.readable:
                            self.readable, self.writable, self.errored = select.select(self.read_list, [], [])
                        # self.info.connect.setblocking(True)
                        recv_len = data
                        # print(type(data), data, flush=True)
                        data = b''
                        data += self.info.connect.recv(4096)
                        # print(len(data), flush=True)
                        # self.info.connect.setblocking(False)
                        while len(data) < recv_len:
                            # data += raw_data                            
                            data += self.info.connect.recv(4096)
                        print('receive len = ', len(data), flush=True)
                        send_data = "done"
                        send_raw_data = pickle.dumps(send_data)
                        self.info.connect.sendall(send_raw_data)
                        # data = pickle.loads(b''.join(data))
                        self.thread_broadcasting = []
                        for client in client_list:
                            if client.sound_socket == None or client is self.info:
                                continue
                            thread = threading.Thread(target = self.broadcast, args=(client.sound_socket, data))
                            thread.setDaemon(True)
                            self.thread_broadcasting.append(thread)
                            thread.start()
                        for thread in self.thread_broadcasting:
                            thread.join()
                            # client.sound_socket.sendall(pickle.dumps(len(data)))
                            # client.sound_socket.sendall(data)
    def broadcast(self, sound_socket, data):
        sound_socket.sendall(pickle.dumps(len(data)))
        recv_raw_data = sound_socket.recv(1024)
        recv_data = pickle.loads(recv_raw_data)
        print(recv_data, flush=True)
        sound_socket.sendall(data)
        recv_raw_data = sound_socket.recv(1024)
        recv_data = pickle.loads(recv_raw_data)
        print(recv_data, flush=True)

    def stop(self):
        self._stop_event.set()
        sys.exit()
if __name__ == "__main__":
    #===== arg parsing ===============
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", help="The IP the server be")
    parser.add_argument("port", type=int, help="port of the IP")
    args = parser.parse_args()
    print(args.IP, args.port)
    #=====Create Socket to listen=====
    IP = args.IP
    Port = args.port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, Port))
    server.listen(5)

    #======client data======== (Todo)
    client_list = list()
    '''
    O)
    Format: [client_info_1 , client_info_2, ...]
    '''

    global client_database
    with open('db.json', 'r+', encoding='utf-8') as f:
        client_database = json.load(f)
        for x in client_database:
            print(x, client_database[x])

    global mic_lock
    mic_lock = threading.Lock()
    #======Start Listening======
    listening = thread_accept_client(server, client_list)
    listening.setDaemon(True)
    listening.start()
    #global thread_list
    thread_list.append(listening)

    ####TODO: ADD SOME CONTROL TO SERVER ex. STOP ALL Client AND QUIT####
    #                                                                   #
    #####################################################################


    #listening.stop()
    while True:
        print(thread_list)
        s = input()
        if s == "quit":
            for i in thread_list:
                #i.asdasd()
                i.stop()
                #i.quit()
                i.join()
    #listening.join()
    
    server.close()
