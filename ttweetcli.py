import socket
import sys
import shlex

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
USERNAME = sys.argv[3]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes('username ' + USERNAME,'UTF-8'))

while True:
    server_data =  client.recv(1024)
    server_message = server_data.decode()
    print(server_message)
    if 'error' == server_message[:5]:
        break
    user_input = input()
    inputSplit = shlex.split(user_input, posix=False)
    if 'tweet' == inputSplit[0]:
        exit = False
        if len(inputSplit) == 3:
            if len(inputSplit[1]) > 152:
                print('message length illegal, connection refused.')
                exit = True
            elif len(inputSplit[1]) < 2:
                print('message format illegal.')
                exit = True
            else: 
                hashtags = inputSplit[2].split('#')
                for tag in hashtags[1:]:
                    if tag.isalnum() == False:
                        print('hashtag illegal format, connection refused.')
                        exit = True 
        if exit:
            break
        else:
            client.sendall(bytes(user_input, 'UTF-8'))
    elif 'getusers' == inputSplit[0]:
        if len(inputSplit) == 1:
            client.sendall(bytes(user_input, 'UTF-8'))
        else:
            print('too many arguments for getusers command')
    elif 'gettweets' == inputSplit[0]:
        if len(inputSplit) == 2:
            client.sendall(bytes(user_input, 'UTF-8'))
        else:
            print('incorrect amount of arguments for getusers command')
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
    if user_input == 'exit':
        client.sendall(bytes(user_input, 'UTF-8'))
        break
client.close()