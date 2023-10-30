#!/usr/bin/env python3 (shabang pre python3)
#env- program, kt. hlada binarku pythonu

#Popis protokolu (| je delimiter, teda oddelovac spravy):
#OPERACIA|sprava(text)

#OPERACIE:   LOGIN|nick
#            SENDMSG|sprava|nick (sprava nemoze obsahovat |)
#            EXIT|nick
#            USERS,nick1,nick2,nick3,.....  #server posiela zoznam pouzivatelov ako odpoved na WHO ↓
#            WHO|nick  #client pyta zoznam prihlasenych pouzivatelov
MSG_SIZE = 100
USERS = list()

import socket as s #to "s" je akoze alias, cize ho budeme vola cez s
from threading import Thread,Lock  #ked mi netreba cely modul

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

def handle_client(client_sock, lock):
    protokol = ChatProtocol("")

    while(True):
        client_msg = client_sock.recv(MSG_SIZE)  # TCP vracia Byte, potrebujeme ich dalej previezt do Stringu
        protokol.parse(client_msg, USERS,client_sock, lock)
    client_sock.close()  # zrusime TCP relaciu voci klientovi


#AF_INET - bude pouzivat ipv4
#SOCK_STREAM - bude pouzivat TCP
#mam vytvoreny TCP socket na IPv4
sock = s.socket(family=s.AF_INET, type=s.SOCK_STREAM)
#keby dam ip adresu 0.0.0.0 tak by pocuval vsetkych
sock.bind(("127.0.0.1", 9999)) #pouzi tuto ip adresu na kt. sa budu klienti pripajat a pouzi konkretny port
sock.listen(10)
#navrat = sock.accept() - je to n-tica
#client_sock = navrat[0]
#client_addr = navrat[1] ↓ skrateny zapis

lock = Lock()

while True:
    (client_sock, client_addr) = sock.accept()
    print("Connected client TCP session created: ({}: {}).".format(client_addr[0], client_addr[1]))

    #toto je volake vlakno
    t = Thread(target=handle_client, args=[client_sock, lock])
    t.run()



sock.close()

