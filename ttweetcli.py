import socket
import sys

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
USERNAME = sys.argv[3]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes(USERNAME,'UTF-8'))

while True:
    server_data =  client.recv(1024)
    print("(server)", server_data.decode())
    user_input = input()
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
    else:
        client.sendall(bytes('none', 'UTF-8'))
client.close()