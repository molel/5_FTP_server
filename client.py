import socket

HOST = '127.0.0.1'
PORT = 9090
EXIT = "exit"

CORRECT_PASSWORD = "Вход выполнен"
sock = socket.socket()
sock.connect((HOST, PORT))
response = ""
while True:
    response = sock.recv(1024).decode()
    print(response, end="")
    if CORRECT_PASSWORD in response:
        break
    print()
    request = input('>')
    sock.send(request.encode())
while True:
    request = input()
    sock.send(request.encode())
    if request == EXIT:
        break
    response = sock.recv(1024).decode()
    print(response, end="")
    response = sock.recv(1024).decode()
    print(response, end="")

sock.close()
