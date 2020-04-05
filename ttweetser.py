import socket, threading
import sys

TIMELINE = {
    '#tag1': ['tweet1']
}
HASHTAGS = {
    'will': ['#tag1']
}

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
        while True:
            data = self.clientSocket.recv(2048)
            clientMessage = data.decode()
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
                break
            print("(client)", clientMessage)
            self.clientSocket.send(bytes(clientMessage, 'UTF-8'))
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