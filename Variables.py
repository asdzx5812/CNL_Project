class States:
    initial = "Initial"
    login = "Login"
    sign_up = "Sign up"
    waiting_for_talk = "Waiting for talk"
    talking = "Talking"

class Client_info():
    def __init__(self, connect, host, port):
        self.connect = connect
        self.host = host
        self.port = port
        self.username = ""
        self.password  = ""
        self.state = States.initial
        self.sound_socket = None
    def print_info(self):
        print("Connect to %s:%d" % (self.host, self.port))
        print("Current state: %s" % self.state)
        print("Username = %s" % self.username)
        print("Password = %s" % self.password)
