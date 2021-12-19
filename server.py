import json
import socket
from datetime import datetime

from fileManager import *
from settings import *


def readAuth(fileName=AUTH):
    with open(fileName, "r", encoding=ENCODING) as file:
        logins = json.load(file)
    return logins


def writeAuth(fileName, data, currentPath=os.getcwd()):
    os.chdir(WORKING_DIRECTORY)
    data.update(readAuth(fileName))
    json.dump(data, open(fileName, "w", encoding=ENCODING), sort_keys=True)
    os.chdir(currentPath)


def writeLog(fileName, text):
    with open(fileName, "a", encoding=ENCODING) as logFile:
        logFile.write(f"{'-' * 25}\n{datetime.now()}: {text}\n")


def requestPassword(sock, conn, correctPassword, login):
    password = makeRequest(conn, REQUEST_PASSWORD)
    if password == correctPassword:
        handle(sock, conn, login)
    else:
        requestPassword(sock, conn, correctPassword, login)


def requestNewPassword(sock, conn, login):
    newPassword = makeRequest(conn, REQUEST_NEW_PASSWORD)
    writeAuth(AUTH, {login: newPassword}, currentPath=os.getcwd())
    handle(sock, conn, login)


def makeRequest(conn, message):
    send(conn, message)
    return recv(conn)


def send(conn, message, encoding=ENCODING):
    conn.send(message.encode(encoding))


def recv(conn: socket.socket, bufSize=BUFFER_SIZE, encoding=ENCODING):
    return conn.recv(bufSize).decode(encoding)


def auth(sock, conn):
    logins = readAuth()
    login = makeRequest(conn, REQUEST_LOGIN)
    if login in logins:
        requestPassword(sock, conn, logins[login], login)
    else:
        requestNewPassword(sock, conn, login)


def accept(sock):
    while True:
        try:
            conn = sock.accept()[0]
            auth(sock, conn)
        except:
            continue


def main():
    os.chdir(WORKING_DIRECTORY)
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(1)
    accept(sock)


if __name__ == '__main__':
    main()
