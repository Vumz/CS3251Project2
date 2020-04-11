import socket
import threading
import sys
import time
import shlex

TIMELINE = {
    #'#tag1': ['tweet1']
}
HASHTAGS = {
    #'will': ['#tag1']
}
TWEETS = {
    #'vamsee': ['test #tag2']
}
TIMELINES = {
    #'vamsee': ['test #tag2']
}
HASHTAGMAP = {
    #'#tag1': ['vamsee']
}
USERS = {
    #'vamsee': []
}


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        print("New connection added: ", clientAddress)
    def run(self):
        print("Connection from : ", clientAddress)
        clientMessage = ''
        user = ''
        while True:
            # send any tweets queued for the user
            if user in USERS and len(USERS[user]) > 0:
                self.clientSocket.sendall(bytes(USERS[user][0], 'UTF-8'))
                print(USERS)
                print(user + ' ' + USERS[user][0])
                del USERS[user][0]
            try:
                data = self.clientSocket.recv(2048)
            except socket.error as ex:
                continue
            # print(data)
            if len(data) == 0:
                clientMessage = 'exit'
            else:
                clientMessage = data.decode()
            messageSplit = shlex.split(clientMessage, posix=False)
            if messageSplit == []:
                messageSplit.append('none')
            # register user
            if 'username' == messageSplit[0]:
                if messageSplit[1] not in USERS:
                    user = messageSplit[1]
                    USERS[user] = []
                    TWEETS[user] = []
                    TIMELINES[user] = []
                    self.clientSocket.sendall(bytes('username legal, connection established.','UTF-8'))
                else:
                    self.clientSocket.sendall(bytes('username illegal, connection refused.', 'UTF-8'))
            # tweet functionality
            elif 'tweet' == messageSplit[0]:
                TWEETS[user].append(user + ': ' + messageSplit[1] + ' ' + messageSplit[2])
                hashtags = messageSplit[2].split('#')
                users_subscribed = set()
                for tag in hashtags[1:]:
                    fullTag = '#' + tag
                    if fullTag in HASHTAGMAP:
                        for u in HASHTAGMAP[fullTag]:
                            users_subscribed.add(u)
                if '#ALL' in HASHTAGMAP:
                    for u in HASHTAGMAP['#ALL']:
                            users_subscribed.add(u)
                for account in users_subscribed:
                    # add tweet to associated timelines
                    if account in TIMELINES:
                        TIMELINES[account].append(user + ': ' + messageSplit[1] + ' ' + messageSplit[2])
                    else:
                        TIMELINES[account] = [user + ': ' + messageSplit[1] + ' ' + messageSplit[2]]
                    # send tweet to whoever is subscribed to hashtags
                    if account in USERS:
                        USERS[account].append(user + ' ' + messageSplit[1] + ' ' + messageSplit[2])
            # getusers functionality
            elif 'getusers' == messageSplit[0]:
                payload = ''
                for username in USERS:
                    payload = payload + username + '\n'
                self.clientSocket.sendall(bytes(payload[:-1], 'UTF-8'))
            # gettweets functionality
            elif 'gettweets' == messageSplit[0]:
                username = messageSplit[1]
                if username in USERS:
                    payload = ''
                    for tweet in TWEETS[username]:
                        payload = payload + tweet + '\n'
                    self.clientSocket.sendall(bytes(payload[:-1], 'UTF-8'))
                else:
                    self.clientSocket.sendall(bytes(('no user ' + username + ' in the system'), 'UTF-8'))
            # timeline functionality
            elif 'timeline' == messageSplit[0]:
                payload = ''
                for tweet in TIMELINES[user]:
                    payload = payload + tweet + '\n'
                self.clientSocket.sendall(bytes(payload[:-1], 'UTF-8'))
            # exit functionality
            elif clientMessage == 'exit':
                if user in USERS:
                    del USERS[user]
                if user in TWEETS:
                    del TWEETS[user]
                if user in HASHTAGS:
                    del HASHTAGS[user]
                if user in TIMELINES:
                    del TIMELINES[user]
                for key, value in HASHTAGMAP.items():
                    if user in value:
                        value.remove(user)
                self.clientSocket.sendall(bytes('bye bye', 'UTF-8'))
                self.clientSocket.close()
                break
            # unsubscribe functionality
            elif 'unsubscribe' == messageSplit[0]:
                print('server unsubscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                if hashtag in HASHTAGS[username]:
                    print("unsubscribing", hashtag)
                    HASHTAGS[username].remove(hashtag)
                    print(HASHTAGS)
                if username in HASHTAGMAP[hashtag]:
                    HASHTAGMAP[hashtag].remove(username)
                    print(HASHTAGMAP)
                self.clientSocket.sendall(bytes('operation success', 'UTF-8'))
            # subscribe functionality
            elif 'subscribe' == messageSplit[0]:
                print('server subscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                if username not in HASHTAGS:
                    HASHTAGS[username] = []
                if len(HASHTAGS[username]) > 2 or hashtag in HASHTAGS[username]:
                    self.clientSocket.sendall(bytes('operation failed: sub ' + hashtag + ' failed, already exists or exceeds 3 limitation', 'UTF-8'))
                else:
                    print("subscribing", hashtag)
                    self.clientSocket.sendall(bytes('operation success', 'UTF-8'))
                    HASHTAGS[username].append(hashtag)
                    if hashtag not in HASHTAGMAP:
                        HASHTAGMAP[hashtag] = []
                    HASHTAGMAP[hashtag].append(username)
                    print(HASHTAGS)
                    print(HASHTAGMAP)
        print("Client at ", clientAddress, " disconnected...")
LOCALHOST = "127.0.0.1"
PORT = int(sys.argv[1])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request..")
while True:
    server.listen(1)
    clientSocket, clientAddress = server.accept()
    clientSocket.setblocking(0)
    newThread = ClientThread(clientAddress, clientSocket)
    newThread.start()
server.close()