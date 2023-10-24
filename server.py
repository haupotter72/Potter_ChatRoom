import socket
import threading
import queue
import json
import time
import os
import os.path
import sys

IP = ''
PORT = 50007
queue = queue.Queue()                  
users = []                             
lock = threading.Lock()                



def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, queue, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        # self.addr = None

   
    def tcp_connect(self, conn, addr):
        #  name
        user = conn.recv(1024)
        user = user.decode()

        # 
        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        # Print new user name
        print(' New connection:', addr, ':', user, end='')
        # refresh user list
        d = onlines()
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)
            conn.close()
        except:
            print(user + ' Connection lose')
            #
            self.delUsers(conn, addr)
            conn.close()

  
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ',
                      end='')
                d = onlines()
                self.recv(d, addr)
                
                print(d)
                break
            a += 1

 
    def recv(self, data, addr):
        lock.acquire()
        try:
            queue.put((addr, data))
        finally:
            lock.release()

   
    def sendData(self):
        while True:
            if not queue.empty():
                data = ''
               
                message = queue.get()
              
                if isinstance(message[1], str):
                    for i in range(len(users)):
                        
                        for j in range(len(users)):
                        
                            if message[0] == users[j][2]:
                                print(
                                    ' this: message is from user[{}]'.format(j))
                                data = ' ' + users[j][1] + '：' + message[1]
                                break
                        users[i][0].send(data.encode())
                # data = data.split(':;')[0]
                if isinstance(message[1], list): 
                  
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):

        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    cserver.start()

    while True:
        time.sleep(1)
        if not cserver.is_alive():
            print("Chat connection lost...")
            sys.exit(0)
