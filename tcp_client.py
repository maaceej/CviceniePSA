#!usr/bin/env python 3

import socket as s
from threading import Lock  #ked mi netreba cely modul


MSG_SIZE = 100

class ChatProtocol:
    def __init__(self, nick):
        self._nick = nick

    def login(self):
        return "LOGIN|{}".format(self._nick).encode()

    def exit(self):
        return "EXIT|{}".format(self._nick).encode()

    def send_msg(self, msg):
        return "SENDMSG|{}|{}".format(self._nick, msg).encode()

    def who(self):
        return "WHO|{}".format(self._nick).encode()

    def users(self, user_list):
        users = ""
        for user in user_list:
            users += user + ","
        if(len(users) > 1):
            users = users[0:len(users)-1] #z users zober od nuly po predposledny
        return "USERS|{}".format(users).encode()



    def parse(self, binary_msg : bytes, user_list : list, client_sock : s.socket, lock : Lock):
        str_msg = binary_msg.decode()
        list_msg_parts = str_msg.split("|")
        if (len(list_msg_parts) > 1):
            nick = list_msg_parts[1]
        if (len(list_msg_parts) > 2):
            message = list_msg_parts[2]

        if list_msg_parts[0] == "LOGIN":
            #volako zamknem tych userov aby iba jeden menil
            lock.acquire()
            user_list.append(nick)
            lock.release()
            print("Client '{}' has been connected".format(nick))
        elif list_msg_parts[0] == "EXIT":
            lock.acquire()
            user_list.remove(nick)
            lock.release()
            print("Client '{}' has been disconnected".format(nick))
        elif list_msg_parts[0] == "SENDMSG":
            print("Client '{}' message: {}".format(nick, message))
        elif list_msg_parts[0] == "WHO":
            print("Client '{}' requested list of users".format(nick))
            client_sock.send(self.users(user_list))
        elif list_msg_parts[0] == "USERS":
            users = nick.split(',')
            print("Logged in users: {}".format(users))


SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

sock = s.socket(family=s.AF_INET, type=s.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))

nick = input("Enter nick: ")
protokol = ChatProtocol(nick)
sock.send(protokol.login())
while True:
    msg = input("Enter message: ")
    if msg[0] == '%':
        if msg[1] == 'q':
            sock.send(protokol.exit())
            sock.close()
            exit(0)
        elif msg[1] == 'w':
            sock.send(protokol.who())
            bin_msg = sock.recv(MSG_SIZE)
            protokol.parse(bin_msg, None, None, None) #zadefinovane uplne hore, konstanta, velkost buffera vlastne


    sock.send(protokol.send_msg(msg))

sock.close()