import socket
import sys

HASHTAGS = []

def subscribe(hashtag):
  if len(HASHTAGS) >= 3:
    print('operation failed: sub',  hashtag, 'failed, already exists or exceeds 3 limitation')
  else:
    print("subscribing", hashtag)
    HASHTAGS.append(hashtag)

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
  client.sendall(bytes(user_input, 'UTF-8'))
  if user_input == 'subscribe':
    subscribe('test')
  if user_input == 'exit':
    break
client.close()
print(HASHTAGS)