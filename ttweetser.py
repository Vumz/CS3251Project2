import socket, threading
import sys

TIMELINE = {
    '#tag1': ['tweet1']
}
HASHTAGS = {
    'will': ['#tag1']
}
TWEETS = {
    'vamsee': ['test #tag2']
}
USERS = set()

def subscribe(username, hashtag):
    if len(HASHTAGS[username]) >= 3 or hashtag in HASHTAGS[username]:
        print('operation failed: sub',  hashtag, 'failed, already exists or exceeds 3 limitation')
    else:
        print("subscribing", hashtag)
        HASHTAGS[username].append(hashtag)
        print(HASHTAGS)

def unsubscribe(username, hashtag):
    if hashtag in HASHTAGS[username]:
        print("unsubscribing", hashtag)
        HASHTAGS[username].remove(hashtag)
        print(HASHTAGS)


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
            data = self.clientSocket.recv(2048)
            clientMessage = data.decode()
            messageSplit = clientMessage.split()
            if 'username' == messageSplit[0]:
                if messageSplit[1] not in USERS:
                    user = messageSplit[1]
                    USERS.add(user)
                    TWEETS[user] = []
                    self.clientSocket.sendall(bytes('username legal, connection established.','UTF-8'))
                else:
                    self.clientSocket.sendall(bytes('error: username has wrong format, connection refused.'))
            elif 'tweet' == messageSplit[0]:
                TWEETS[user].append(messageSplit[1] + ' ' + messageSplit[2])
            elif 'getusers' == messageSplit[0]:
                for username in USERS:
                    self.clientSocket.sendall(bytes(username, 'UTF-8'))
            elif 'gettweets' == messageSplit[0]:
                username = messageSplit[1]
                if username in USERS:
                    for tweet in TWEETS[username]:
                        self.clientSocket.sendall(bytes(tweet, 'UTF-8'))
                else:
                    self.clientSocket.sendall(bytes(('no user ' + username + ' in the system'), 'UTF-8'))
            if 'unsubscribe' in clientMessage:
                print('server unsubscribing')
                name_index = clientMessage.index(',') + 1
                tag_index = clientMessage.index('#')
                username = clientMessage[name_index:tag_index - 1]
                hashtag = clientMessage[tag_index:]
                unsubscribe(username, hashtag)
            elif 'subscribe' in clientMessage:
                print('server subscribing')
                name_index = clientMessage.index(',') + 1
                tag_index = clientMessage.index('#')
                username = clientMessage[name_index:tag_index - 1]
                hashtag = clientMessage[tag_index:]
                subscribe(username, hashtag)
            if clientMessage == 'exit':
                USERS.remove(user)
                del TWEETS[user]
                del HASHTAGS[user]
                self.clientSocket.sendall(bytes('bye bye', 'UTF-8'))
                break
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