import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import tkinter.filedialog as fd
from PIL import ImageTk, Image
#import recorder
import threading
#import pyaudio
import wave
import argparse
import client
import re
import sounddevice as sd
import numpy as np 
import scipy.io.wavfile as wav 
from Variables import States
import pickle
import select
import time

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('300x500')
        self.title('CNL Walkie-Talkie')
        self.resizable(0, 0)
        self._frame = None
        self.switch_frame(StartPage)

        # socket init
        self.client = client.build_connection(args)
        send_data = "New"
        send_raw_data = send_data.encode('utf-8')
        self.client.connect.sendall(send_raw_data)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        # GUI is master
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.bg_color = 'DeepSkyBlue2'
        self.master.configure(bg = self.bg_color)
        self.configure(bg = self.bg_color)  

        tk.Label(self, bg = self.bg_color).grid(row = 0, column = 0, columnspan=4, rowspan = 1, pady = 2)
        tk.Label(self, text="CNL", font=('Helvetica', 42, "bold"), bg = self.bg_color).grid(row = 1, column = 0, columnspan=4, rowspan = 2)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold"), bg = self.bg_color).grid(row = 4, columnspan=4, rowspan = 2) 
        tk.Label(self, bg = self.bg_color).grid(row = 6, column = 0, columnspan=4, rowspan = 1, pady = 0)       

        # username
        self.username = tk.StringVar()
        tk.Label(self, text="--- Username ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 8, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.username).grid(row = 10, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 11, column = 0, columnspan=4, rowspan = 2)

        # password
        self.password = tk.StringVar()
        tk.Label(self, text="--- Password ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 12, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password, show="\u2022").grid(row = 14, columnspan=4, pady = 5)


        tk.Label(self, bg = self.bg_color).grid(row = 15, column = 0, columnspan=4, rowspan = 1, pady = 5)

        # login
        tk.Button(self, text="Login", font=('Helvetica', 12, "bold"), width = 16, command=self.login).grid(row = 16, column = 0, columnspan=4, pady = 10)

        # reigster
        tk.Button(self, text="Register", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(RegisterPage)).grid(row = 17, column = 0, columnspan=4, pady = 5)

    def login(self):
        usrname = self.username.get()
        passwd = self.password.get()
        print("self.username.get():", usrname)
        print("self.password.get():", passwd)
        if(not re.match("^[A-Za-z0-9_]+$", usrname) or not re.match("^[A-Za-z0-9_]+$", passwd)):
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Username or Password contains invalid characters.\n         (letters, numbers and underscores only.)", font=('Helvetica'))
            label.pack(side="top", fill="x", pady=20)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        else:
            if client.Login(self.master.client, usrname, passwd):
                self.master.client.username = usrname
                self.master.switch_frame(MainPage)
            else:
                popup = tk.Tk()
                popup.wm_title("Error")
                label = ttk.Label(popup, text="Wrong Username or Password", font=('Helvetica'))
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
                B1.pack()
                popup.mainloop()


class RegisterPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.bg_color = 'DeepSkyBlue2'
        self.master.configure(bg = self.bg_color)
        self.configure(bg = self.bg_color)

        tk.Label(self, bg = self.bg_color).grid(row = 0, column = 0, columnspan=4, rowspan = 1, pady = 0) 
        tk.Label(self, text="Please enter", font=('Helvetica', 16, "bold"), bg = self.bg_color).grid(row = 2, columnspan=4, rowspan = 1) 
        tk.Label(self, text="following informations.", font=('Helvetica', 16, "bold"), bg = self.bg_color).grid(row = 3, columnspan=4, rowspan = 1) 
        tk.Label(self, bg = self.bg_color).grid(row = 4, column = 0, columnspan=4, rowspan = 1, pady = 1)     

        # username
        self.username = tk.StringVar()
        tk.Label(self, text="--- Username ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 5, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.username).grid(row = 7, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 8, column = 0, columnspan=4, rowspan = 2)

        # password
        self.password = tk.StringVar()
        tk.Label(self, text="--- Password ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 9, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password, show="\u2022").grid(row = 11, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 12, column = 0, columnspan=4, rowspan = 2)

        # password again
        self.password_confirm = tk.StringVar()
        tk.Label(self, text="--- Password Again ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 13, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password_confirm, show="\u2022").grid(row = 15, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 16, column = 0, columnspan=4, rowspan = 1, pady = 2)

        # reigster
        tk.Button(self, text="Register", font=('Helvetica', 12, "bold"), width = 16, command=self.reigster).grid(row = 17, column = 0, columnspan=4, pady = 5)

        # Back to login
        tk.Button(self, text="Back", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(StartPage)).grid(row = 18, column = 0, columnspan=4, pady = 10)


    def reigster(self):
        usrname = self.username.get()
        passwd = self.password.get()
        password_confirm = self.password_confirm.get()
        print("self.username.get():", usrname)
        print("self.password.get():", passwd)
        print("self.password_confirm.get():", password_confirm)

        if passwd != password_confirm:
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Passwords are not same, please enter again.", font=('Helvetica'))
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        elif(not re.match("^[A-Za-z0-9_]+$", usrname) or not re.match("^[A-Za-z0-9_]+$", passwd)):
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Username or Password contains invalid characters.\n(letters, numbers and underscores only.)", font=('Helvetica'), anchor='center', justify = 'center')
            label.pack(side="top", fill="x", pady=20)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        else:
            if client.Sign_up(self.master.client, usrname, passwd, password_confirm):
                popup = tk.Tk()
                popup.wm_title("Congratulations!") 
                label = ttk.Label(popup, text="Your registration has completed.\nWelcome!", font=('Helvetica'), anchor='center', justify = 'center')
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Login now", command = popup.destroy)
                B1.pack()
                self.master.switch_frame(StartPage)
            else:
                popup = tk.Tk()
                popup.wm_title("Sorry")
                label = ttk.Label(popup, text="The account has been used.", font=('Helvetica'))
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
                B1.pack()
                popup.mainloop()

class thread_recv_sound(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stopping Thread
        self.socket = client_socket
        self.read_list = [client_socket]

    def run(self):
        fs = 44100 
        while(self._stop_event.is_set() == False):
            self.readable, self.writable, self.errored = select.select(self.read_list, [], [])
            if self.socket in self.readable:
                recv_data = self.socket.recv(4096)
                send_data = "start"
                send_raw_data = pickle.dumps(send_data)
                self.socket.sendall(send_raw_data)
                recv_data = pickle.loads(recv_data)
                print('Other person is talking', recv_data, flush=True)
                #recv_data = recv_data.decode()
                recv_len = recv_data
                data = b''
                data += self.socket.recv(4096)
                # print(len(data), flush=True)
                # self.info.connect.setblocking(False)
                while len(data) < recv_len:
                    # data += raw_data                            
                    data += self.socket.recv(4096)
                print('receive len = ', len(data), flush=True)
                
                data = pickle.loads(data)
                print(data, flush=True)
                sd.play(data, fs)
                sd.wait()
                send_data = "done"
                send_raw_data = pickle.dumps(send_data)
                self.socket.sendall(send_raw_data)
                '''
                Processing Data....

                Todo:
                
    /
                '''
    def stop(self):
        self._stop_event.set()

class MainPage(tk.Frame):
    def __init__(self, master):
        master.client.state = States.waiting_for_talk
        tk.Frame.__init__(self, master)
        self.running = None
        self.click = False
        self.bg_color = 'DeepSkyBlue2'
        self.configure(bg = self.bg_color) 
        tk.Label(self, bg = self.bg_color).grid(row = 0, rowspan = 1, pady = 5)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold"), bg = self.bg_color).grid(row = 1, pady = 5)
        self.photo = ImageTk.PhotoImage(file = "record.png")
        self.record_button = tk.Button(self, text="record!", image = self.photo, bg = self.bg_color)
        self.record_button.grid(row = 2, pady = 5)
        
        self.record_button.bind('<ButtonPress-1>', lambda event: self.Ask_for_mic())#self.start_recording())
        self.record_button.bind('<ButtonRelease-1>', lambda event: self.release_and_stop())
        self.logout_button = tk.Button(self, text="logout", command=self.logout)
        self.logout_button.grid(row = 3, pady = 20)

        self.audio_socket = client.build_connection(args)
        send_data = self.master.client.username
        print("while building second connect",send_data, flush=True)
        send_raw_data = send_data.encode('utf-8')
        self.audio_socket.connect.sendall(send_raw_data)
        self.recv_sound = thread_recv_sound(self.audio_socket.connect)
        self.recv_sound.start()
        self.get_mic = False
        print("??", flush=True)


    def logout(self):
        client.logout(self.master.client)
        self.master.switch_frame(StartPage)

    def Ask_for_mic(self):
        send_data = "Req"
        send_raw_data = pickle.dumps(send_data)
        #send_raw_data = send_data.encode("utf-8")
        self.master.client.connect.sendall(send_raw_data)
        recv_raw_data = self.master.client.connect.recv(1024)
        recv_data = pickle.loads(recv_raw_data)
        #recv_data = recv_raw_data.decode("utf-8")
        state, data = recv_data.split(":")
        if data == "Mic_ACK":
            print("Get_Mic", flush=True)
            self.get_mic = True
            thread_recording = threading.Thread(target = self.create_recording_thread)
            thread_recording.setDaemon(True)
            thread_recording.start()
            # self.create_recording_thread()
        else:
            popup = tk.Tk()
            popup.wm_title("Sorry") 
            label = ttk.Label(popup, text="Someone is talking.\n", font=('Helvetica'), anchor='center', justify = 'center')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Try later", command = popup.destroy)
            B1.pack()



    def create_recording_thread(self):
        print('==========start recording==========', flush=True)
        channels = 1
        fs = 44100  # Record at 44100 samples per second
        duration = 3
        # self.recording_threads = []
        self.recordings = []
        self.thread_recording = threading.Thread(target = self.start_recording)
        self.thread_recording.setDaemon(True)
        # self.recording_threads.append(thread_recording)
        self.thread_recording.start()
        # time.sleep(duration)
        while self.get_mic:
            # print("get_mic:", self.get_mic)
            my_recording = sd.rec(int(duration*fs), samplerate=fs, channels=channels, dtype='float64')
            # print(type(my_recording))
            print("Is recording")
            sd.wait(ignore_errors=False)
            # sd.play(self.my_recording, fs)
            # sd.wait()
            # print("done", flush= True)
            send_raw_data = pickle.dumps(my_recording)
            self.recordings.append(send_raw_data)

        self.thread_recording.join()
        send_data = "quit"
        send_raw_data = pickle.dumps(send_data)
        self.master.client.connect.sendall(send_raw_data)
        recv_raw_data = self.master.client.connect.recv(1024)
        recv_data = pickle.loads(recv_raw_data)
        state, data = recv_data.split(":")
        exit()

    def start_recording(self):                   
        while len(self.recordings) > 0 or self.get_mic:
            if len(self.recordings) > 0:
                # print(self.my_recording, flush=True)
                send_raw_data = self.recordings[0]
                self.recordings.pop(0)
                send_len = len(send_raw_data)
                send_len = pickle.dumps(send_len)
                self.master.client.connect.sendall(send_len) 
                recv_raw_data = self.master.client.connect.recv(1024)
                recv_data = pickle.loads(recv_raw_data)
                print(recv_data, flush=True)
                self.master.client.connect.sendall(send_raw_data)
                recv_raw_data = self.master.client.connect.recv(1024)
                recv_data = pickle.loads(recv_raw_data)
                print(recv_data, flush=True)

        

    def release_and_stop(self):
        if self.get_mic :
            self.get_mic = False
            print('==========stop recording==========', flush=True)
            
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="port of the IP")
    global args
    args = parser.parse_args()

    app = GUI()
    app.mainloop()
