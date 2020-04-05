import socket, threading
import sys
import shlex

TIMELINE = {
    '#tag1': [('sender', 'tweet1'), ('sender2', 'tweet2')],
    '#tag2': [('s1', 't1'), ('s2', 't2')]
}
HASHTAGS = {
    'will': ['#tag1']
}

def subscribe(username, hashtag):
    if username not in HASHTAGS:
        HASHTAGS[username] = []
    if len(HASHTAGS[username]) >= 3 or hashtag in HASHTAGS[username]:
        print('operation failed: sub', hashtag, 'failed, already exists or exceeds 3 limitation')
    else:
        print("subscribing", hashtag)
        HASHTAGS[username].append(hashtag)
        print(HASHTAGS)

def unsubscribe(username, hashtag):
    if hashtag in HASHTAGS[username]:
        print("unsubscribing", hashtag)
        HASHTAGS[username].remove(hashtag)
        print(HASHTAGS)

def timeline(username):
    if username not in HASHTAGS:
        return
    subscriptions = HASHTAGS[username]
    timeline = []
    if '#ALL' in subscriptions:
        for tag in TIMELINE.keys():
            tweets = TIMELINE[tag]
            for tweet in tweets:
                sender, message = tweet
                timeline.append(format_tweet(sender, message, tag))
    else:
        for sub in subscriptions:
            if sub in TIMELINE:
                for tag in TIMELINE.keys():
                    tweets = TIMELINE[tag]
                    for tweet in tweets:
                        sender, message = tweet
                        timeline.append(format_tweet(sender, message, tag))

    return timeline
    

def format_tweet(sender, message, hashtag):
    return sender + ': "' + message + '" ' + hashtag + '\n'

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
            messageSplit = clientMessage.split()
            if 'unsubscribe' == messageSplit[0]:
                print('server unsubscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                unsubscribe(username, hashtag)
            elif 'subscribe' == messageSplit[0]:
                print('server subscribing')
                username = messageSplit[1]
                hashtag = messageSplit[2]
                subscribe(username, hashtag)
            elif 'timeline' == messageSplit[0]:
                username = messageSplit[1]
                user_timeline = timeline(username)
                clientMessage = ''
                for tweet in user_timeline:
                    self.clientSocket.send(bytes(tweet, 'UTF-8'))
            elif clientMessage == 'exit':
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