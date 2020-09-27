import socket
import threading
import getpass
import argparse
import time
import re
from Variables import States, Client_info
import sounddevice as sd
import pickle
def Sign_up(client, Username, Password, CheckPassword):
    client.print_info()
    send_data = States.sign_up
    
    send_raw_data = pickle.dumps(send_data)
    #send_raw_data = send_data.encode("utf-8")
    client.connect.sendall(send_raw_data)
    recv_raw_data = client.connect.recv(1024)
    
    recv_data = pickle.loads(recv_raw_data)
    #recv_data = recv_raw_data.decode("utf-8")
    state, msg = recv_data.split(":")
#    if state != States.sign_up:
#        print("Somethings went wrong while sign up")
#        return
    
    print(recv_data, 'Now sign up:')   
    send_data = Username + ',' + Password
    
    send_raw_data = pickle.dumps(send_data)
    #send_raw_data = send_data.encode('utf-8')
    client.connect.sendall(send_raw_data)
    recv_raw_data = client.connect.recv(1024)
    recv_data = pickle.loads(recv_raw_data)
    
    #recv_data = recv_raw_data.decode("utf-8")
    state, msg = recv_data.split(":")
    if msg == "Ent":
        print("Sign up successfully!!")
        return True
    elif msg == "Rej":
        print("The account has been used.")   
        return False
    else:
        print("Something in client went wrong.")
        return False

def Login(client, username, password):
    client.print_info()
    send_data = States.login
    
    send_raw_data = pickle.dumps(send_data)
    #send_raw_data = send_data.encode("utf-8")
    client.connect.sendall(send_raw_data)
    
    recv_raw_data = client.connect.recv(1024)
    
    recv_data = pickle.loads(recv_raw_data)
    #recv_data = recv_raw_data.decode("utf-8")
    print('Now login:', recv_data)
    send_data = username + "," + password
    
    send_raw_data = pickle.dumps(send_data)
    #send_raw_data = send_data.encode('utf-8')
    print("send for login",send_data)
    client.connect.sendall(send_raw_data)
    recv_raw_data = client.connect.recv(1024)
    recv_data = pickle.loads(recv_raw_data)
    #recv_data = recv_raw_data.decode("utf-8")
    print(send_data, recv_data)
    state, msg = recv_data.split(":")
   ############################################
    if state == States.waiting_for_talk:
        print("Login successfully!!")
        return True
    else:
        print("Username or password isn't correct.")
        return False



def build_connection(args):
    IP = args.IP
    port = args.port
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client_info(connection, IP, port)
    client.connect.connect((IP, port))
    return client

def logout(client):
    send_data = "quit"

    send_raw_data = pickle.dumps(send_data)
    #send_raw_data = send_data.encode('utf-8')
    client.connect.sendall(send_raw_data)
    recv_raw_data = client.connect.recv(1024)
    recv_data = pickle.loads(recv_raw_data)
    #recv_data = recv_raw_data.decode("utf-8")
    state, msg = recv_data.split(":")
    print(state, ":", msg)
    

if __name__ == "__main__":
    #====== arg parsing =========
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="port of the IP")
    args = parser.parse_args()
    main(args)
    
def main(args):
    print(args.IP, args.port)
    #======Connect to Server=====
    #IP = args.IP
    #port = args.port
    #connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client = Client_info(connection, IP, port)
    #client.connect.connect((IP, port)) #Server IP & Port
    # Before login
    # Check operation
    recv_raw_data = client.connect.recv(1024)
    recv_data = recv_raw_data.decode("utf-8")
    print("Welcome Data:", recv_data)
    state = recv_data.split(":")[0]
    while True:
        #TODO: make the initial operation into a function and make everything into this loop
        if state == States.initial:
            operation = input("Please input the operation:('sign up'/'login'/'quit'):")
            if operation == "quit":
                print("Goodbye~")
                client.connect.sendall(operation.encode("utf-8"))
                client.connect.close()
                client.states = "quit"
                break
            elif operation == "sign up":
                state = Sign_up(client)
            elif operation == "login":
                state = Login(client)
            else:
                print("Unknown command")

        elif state == States.waiting_for_talk:
            #TODO: Create another socket to recv msg.#########
            #recv_sound = thread_recv_sound(client.connect)  #
            #recv_sound.start()                              #
            ##################################################
            print("Strat to talk")
            while True:
                key = input("0 for quit, 1 for talk:") #Change to Input Key
                if(key == '0'): #Client quit
                    client.connect.sendall(b'quit')
                    recv_raw_data = client.connect.recv(1024)
                    recv_data = recv_raw_data.decode("utf-8")
                    print(recv_data)
                    state, msg = recv_data.split(":")
                    break
                elif(key == '1'): #Ask for Mic
                    client.connect.sendall(b'Req')
                    recv_raw_data = client.connect.recv(1024)
                    recv_data = recv_raw_data.decode("utf-8")
                    print(recv_data)
                    state, msg = recv_data.split(":")
                    if (msg == 'Mic_ACK'):
                        for msg in range(2):  #Change this to vocal file
                            data = input("Talking...... :")
                            data = data.encode('utf-8')
                            client.connect.sendall(data)
                        time.sleep(0.1)
                        data = 'quit'
                        data = data.encode('utf-8')
                        client.connect.sendall(data)
                    elif (msg == 'Mic_REJ'):
                        print('Microphone Reject') #Wait a second
                        sleep(1)


    #print("Login or Sign up successfully")
    '''
    ##############################################
    #======Create Thread to Recieve msg======
    # start recording
    # Maybe this line can put in the Sign_up or Login
    recv_sound = thread_recv_sound(client)
    recv_sound.start()

    while True:
        key = "" #Input Key
        if(key == ''): #Client quit
            break
        elif(key == ''): #Ask for Mic
            client.sendall(b'REQ')
            data = client.recv(1024)
            if (data == b'MIC_ACK'):
                data = input()#Change this to vocal
                data = data.encode('utf-8')
                clent.sendall(data)
            elif (data == b'MIC_REJ'):
                print('Microphone Reject') #Wait a second
                sleep(1)

    recv_sound.stop()
    recv_sound.join()
    
    client.sendall(b'quit')
    '''
    #client.close()

