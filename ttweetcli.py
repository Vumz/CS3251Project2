import socket
import sys
import shlex
import threading
import time
import os

def printServer(client):
    while True:
        server_data =  client.recv(1024)
        server_message = server_data.decode()
        print(server_message)
        # exit if error message recieved from server
        if 'error' == server_message[:5]:
            client.sendall(bytes('exit', 'UTF-8'))
            client.close()
            os._exit(os.EX_OK)

# check for the inital correct amount of arguments
if len(sys.argv) != 4:
    print('error: args should contain <ServerIP> <ServerPort> <Username>')
    sys.exit()
SERVER = sys.argv[1]
PORT = int(sys.argv[2])
USERNAME = sys.argv[3]
# check if server IP valid
unitsIP = SERVER.split('.')
if len(unitsIP) != 4:
    print('error: server ip invalid, connection refused.')
    sys.exit()
for unit in unitsIP:
    if int(unit) < 0 or int(unit) > 255:
        print('error: server ip invalid, connection refused.')
        sys.exit()
# check if server port valid
if PORT < 1024 or PORT > 65535:
    print('error: server port invalid, connection refused.')
    sys.exit()
# try initiating a connection with the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER, PORT))
except:
    print('error: server port invalid, connection refused.')
    client.close()
    sys.exit()
client.sendall(bytes('username ' + USERNAME,'UTF-8'))

inputThread = threading.Thread(target=printServer, args=(client,))
inputThread.daemon = True
inputThread.start()

while True:
    user_input = input()
    inputSplit = shlex.split(user_input, posix=False)
    # tweet functionality
    if 'tweet' == inputSplit[0]:
        exit = False
        if len(inputSplit) == 3:
            if len(inputSplit[1]) > 152:
                print('message length illegal, connection refused.')
                exit = True
            elif len(inputSplit[1]) <= 2:
                print('message format illegal.')
                exit = True
            else: 
                hashtags = inputSplit[2].split('#')
                for tag in hashtags[1:]:
                    if tag.isalnum() == False:
                        print('hashtag illegal format, connection refused.')
                        exit = True 
        if exit:
            client.sendall(bytes('exit', 'UTF-8'))
            break
        else:
            client.sendall(bytes(user_input, 'UTF-8'))
    # getusers functionality
    elif 'getusers' == inputSplit[0]:
        if len(inputSplit) == 1:
            client.sendall(bytes(user_input, 'UTF-8'))
        else:
            print('too many arguments for getusers command')
    # gettweets functionality
    elif 'gettweets' == inputSplit[0]:
        if len(inputSplit) == 2:
            client.sendall(bytes(user_input, 'UTF-8'))
        else:
            print('incorrect amount of arguments for getusers command')
    # timeline functionality
    elif 'timeline' == inputSplit[0]:
        if len(inputSplit) == 1:
            client.sendall(bytes(user_input, 'UTF-8'))
        else:
            print('incorrect amount of arguments for timeline command')
    # exit functionality
    elif 'exit' == inputSplit[0]:
        if len(inputSplit) == 1:
            client.sendall(bytes(user_input, 'UTF-8'))
            break
        else:
            print('incorrect amount of arguments for exit command')
    if 'unsubscribe' in user_input:
        if '#' in user_input:
            start = user_input.index('#')
            hashtag = user_input[start:]
            client_message = 'unsubscribe,' + USERNAME + ',' + hashtag
            client.sendall(bytes(client_message, 'UTF-8'))
        else:
            client.sendall(bytes('none', 'UTF-8'))
    elif 'subscribe' in user_input:
        if '#' in user_input:
            start = user_input.index('#')
            hashtag = user_input[start:]
            client_message = 'subscribe,' + USERNAME + ',' + hashtag
            client.sendall(bytes(client_message, 'UTF-8'))
        else:
            client.sendall(bytes('none', 'UTF-8'))
client.close()
sys.exit()