import socket
import threading
import sys
import time

HASHTAGS = {
    # 'will': ['#tag1']
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

def subscribe(username, hashtag):
    if username not in HASHTAGS:
        HASHTAGS[username] = []
    if len(HASHTAGS[username]) > 2 or hashtag in HASHTAGS[username]:
        print('operation failed: sub',  hashtag, 'failed, already exists or exceeds 3 limitation')
    else:
        print("subscribing", hashtag)
        HASHTAGS[username].append(hashtag)
        if hashtag not in HASHTAGMAP:
            HASHTAGMAP[hashtag] = []
        HASHTAGMAP[hashtag].append(username)
        print(HASHTAGS)
        print(HASHTAGMAP)

def unsubscribe(username, hashtag):
    if hashtag in HASHTAGS[username]:
        print("unsubscribing", hashtag)
        HASHTAGS[username].remove(hashtag)
        print(HASHTAGS)
    if username in HASHTAGMAP[hashtag]:
        HASHTAGMAP[hashtag].remove(username)
        print(HASHTAGMAP)


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
                del USERS[user][0]
            data = self.clientSocket.recv(2048)
            clientMessage = data.decode()
            messageSplit = clientMessage.split()
            if messageSplit == []:
                messageSplit.append('none')
            # register user
            print(messageSplit)
            if 'username' == messageSplit[0]:
                if messageSplit[1] not in USERS:
                    user = messageSplit[1]
                    USERS[user] = []
                    TWEETS[user] = []
                    self.clientSocket.sendall(bytes('username legal, connection established.','UTF-8'))
                else:
                    self.clientSocket.sendall(bytes('error: username has wrong format, connection refused.', 'UTF-8'))
            # tweet functionality
            elif 'tweet' == messageSplit[0]:
                TWEETS[user].append(messageSplit[1] + ' ' + messageSplit[2])
                hashtags = messageSplit[2].split('#')
                for tag in hashtags[1:]:
                    if tag in HASHTAGMAP:
                        for account in HASHTAGMAP[tag]:
                            # add tweet to associated timelines
                            if account in TIMELINES:
                                TIMELINES[account].append(messageSplit[1] + ' ' + messageSplit[2])
                            else:
                                TIMELINES[account] = [messageSplit[1] + ' ' + messageSplit[2]]
                            # send tweet to whoever is subscribed to hashtags
                            if account in USERS:
                                USERS[account].append(messageSplit[1] + ' ' + messageSplit[2])
            # getusers functionality
            elif 'getusers' == messageSplit[0]:
                for username in USERS:
                    self.clientSocket.sendall(bytes(username, 'UTF-8'))
            # gettweets functionality
            elif 'gettweets' == messageSplit[0]:
                username = messageSplit[1]
                if username in USERS:
                    for tweet in TWEETS[username]:
                        self.clientSocket.sendall(bytes(tweet, 'UTF-8'))
                else:
                    self.clientSocket.sendall(bytes(('no user ' + username + ' in the system'), 'UTF-8'))
            # timeline functionality
            elif 'timeline' == messageSplit[0]:
                for tweet in TIMELINES[user]:
                    self.clientSocket.sendall(bytes(tweet, 'UTF-8'))
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
                break
            # unsubscribe functionality
            elif 'unsubscribe' == messageSplit[0]:
                print('server unsubscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                unsubscribe(username, hashtag)
            # subscribe functionality
            elif 'subscribe' == messageSplit[0]:
                print('server subscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                subscribe(username, hashtag)

            print("(client)", clientMessage)
            # self.clientSocket.send(bytes(clientMessage, 'UTF-8'))
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
    newThread = ClientThread(clientAddress, clientSocket)
    newThread.start()