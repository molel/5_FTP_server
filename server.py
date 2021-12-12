import json
import shutil
import socket
from datetime import datetime

from settings import *

LOG = WORKING_DIRECTORY + SEP + "log.txt"
ROOT = WORKING_DIRECTORY
CURRENT_PATH = ROOT
LOGIN = " "
ADMIN = "admin"
IS_ADMIN = False
MAX_DIRECTORY_SIZE = 50


def dirSize(path_):
    size = 0
    for path, dirs, files in os.walk(path_):
        for dir_ in dirs:
            size += dirSize(os.path.join(path, dir_))
        for file in files:
            size += os.path.getsize(os.path.join(path, file))
    return size


def checkPath(path):
    return ROOT in os.path.abspath(path) or IS_ADMIN


def pwd():
    path = os.getcwd().replace(ROOT, "")
    if path == "":
        path = "\\"
    return path + "\n"


def ls():
    return "\n".join(os.listdir(CURRENT_PATH)) + "\n"


def cd(path, isAdmin=False):
    global CURRENT_PATH
    if path == "~":
        path = ROOT
    if (checkPath(path) or isAdmin is True) and os.path.isdir(path):
        os.chdir(path)
        CURRENT_PATH = os.path.join(CURRENT_PATH, path)
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def mkdir(path):
    if checkPath(path) or IS_ADMIN:
        os.mkdir(path)
        if dirSize(ROOT) > MAX_DIRECTORY_SIZE:
            rm(path)
            return LACK_OF_MEMORY + "\n"
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def mv(source, destination):
    if checkPath(source) and checkPath(destination) and os.path.exists(source):
        shutil.move(source, destination)
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def rm(path):
    if checkPath(path) and os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def cat(path):
    if checkPath(path) and os.path.exists(path):
        return open(path, "r", encoding=ENCODING).read() + "\n"
    else:
        return INCORRECT_PATH + "\n"


def touch(path):
    if checkPath(path):
        if not path.endswith(".txt"):
            path += ".txt"
        open(path, "a", encoding=ENCODING).close()
        if dirSize(ROOT) > MAX_DIRECTORY_SIZE:
            rm(path)
            return LACK_OF_MEMORY + "\n"
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def write(*args):
    path, text = args[0], " ".join(args[1:])
    if checkPath(path) and os.path.isfile(path):
        tempText = open(path, "r", encoding=ENCODING).read()
        open(path, "a", encoding=ENCODING).write(text)
        if dirSize(ROOT) > MAX_DIRECTORY_SIZE:
            with open(path, "w", encoding=ENCODING) as file:
                file.write(tempText.replace(text, "", (tempText.count(text) - 1)))
                return LACK_OF_MEMORY + "\n"
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def cp(source, destination):
    if checkPath(source) and checkPath(destination) and os.path.exists(source):
        shutil.copy(source, destination)
        if dirSize(ROOT) > MAX_DIRECTORY_SIZE:
            rm(os.path.join(destination, source))
            return LACK_OF_MEMORY + "\n"
        return "\n"
    else:
        return INCORRECT_PATH + "\n"


def free():
    return f"Всего места: {MAX_DIRECTORY_SIZE}\nСвободно: {MAX_DIRECTORY_SIZE - dirSize(ROOT)}\n"


def help_():
    return "pwd - выводит путь текущего каталога\n" \
           "ls DIRECTORY- выводит содержимое каталога\n" \
           "cd DIRECTORY- изменяет текущий каталог\n" \
           "mkdir DIRECTORY - создает каталог\n" \
           "rm PATH - удаляет директорию или каталог\n" \
           "mv SOURCE DESTINATION - перемещает или переименовывает файл\n" \
           "cat FILE - выводит содержимое файла\n" \
           "touch FILE - создает пустой файл\n" \
           "write FILE TEXT - добавляет текст в файл\n" \
           "cp SOURCE DESTINATION - копирует файл\n" \
           "free - выводит информацию о памяти" \
           "exit - разрыв соединения с сервером\n" \
           "help - выводит справку по командам\n"


def process(request):
    command, *args = request.split(" ")

    writeLog(LOG, f"От пользователя {LOGIN} получено '{request}'")

    try:
        response = COMMANDS[command](*args)
    except:
        response = "incorrect request\n"

    writeLog(LOG, f"Пользователю {LOGIN} отправлено '{response}'")

    return response


def readAuth(fileName, currentPath=os.getcwd()):
    os.chdir(WORKING_DIRECTORY)
    with open(fileName, "r", encoding=ENCODING) as file:
        logins = json.load(file)
    os.chdir(currentPath)
    return logins


def writeAuth(fileName, data, currentPath=os.getcwd()):
    os.chdir(WORKING_DIRECTORY)
    data.update(readAuth(fileName, currentPath=os.getcwd()))
    json.dump(data, open(fileName, "w", encoding=ENCODING), sort_keys=True)
    os.chdir(currentPath)


def writeLog(fileName, text):
    with open(fileName, "a", encoding=ENCODING) as logFile:
        logFile.write(f"{'-' * 25}\n{datetime.now()}: {text}\n")


def checkDirectory(login):
    global ROOT, SEP, CURRENT_PATH
    if not os.path.exists(ROOT + SEP + login) or not os.path.isdir(ROOT + SEP + login):
        os.mkdir(login)
    ROOT += SEP + login
    cd(login, True)


def handle(sock, conn):
    global IS_ADMIN, LOGIN, ROOT, CURRENT_PATH

    IS_ADMIN = LOGIN == ADMIN
    if LOGIN == ADMIN:
        LOGIN = "$" + LOGIN

    send(conn, CORRECT_PASSWORD + "\n" + LOGIN + ":" + pwd()[:-1] + ">")
    writeLog(LOG, f"Пользователь {LOGIN} авторизовался")
    while True:
        try:
            request = recv(conn)
            if request == "exit":
                conn.close()
            response = process(request)
            send(conn, response)
            send(conn, LOGIN + ":" + pwd()[:-1] + ">")
        except:
            break

    os.chdir(WORKING_DIRECTORY)
    ROOT = WORKING_DIRECTORY
    CURRENT_PATH = ROOT
    conn.close()
    accept(sock)


def requestPassword(sock, conn, correctPassword):
    password = makeRequest(conn, REQUEST_PASSWORD)
    if password == correctPassword:
        handle(sock, conn)
    else:
        requestPassword(sock, conn, correctPassword)


def requestNewPassword(sock, conn, login):
    newPassword = makeRequest(conn, REQUEST_NEW_PASSWORD)
    writeAuth(AUTH, {login: newPassword}, currentPath=os.getcwd())
    handle(sock, conn)


def makeRequest(conn, message):
    send(conn, message)
    return recv(conn)


def send(conn, message, encoding=ENCODING):
    conn.send(message.encode(encoding))


def recv(conn: socket.socket, bufSize=BUFFER_SIZE, encoding=ENCODING):
    return conn.recv(bufSize).decode(encoding)


def auth(sock, conn):
    global LOGIN
    logins = readAuth(AUTH, os.getcwd())
    login = makeRequest(conn, REQUEST_LOGIN)
    checkDirectory(login)
    LOGIN = login
    if login in logins:
        requestPassword(sock, conn, logins[login])
    else:
        requestNewPassword(sock, conn, login)


def accept(sock):
    while True:
        try:
            conn = sock.accept()[0]
            auth(sock, conn)
        except:
            continue


COMMANDS = {
    "pwd": pwd,
    "ls": ls,
    "cd": cd,
    "mkdir": mkdir,
    "rm": rm,
    "mv": mv,
    "cat": cat,
    "touch": touch,
    "write": write,
    "cp": cp,
    "free": free,
    "help": help_
}


def main():
    cd(ROOT, True)
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(1)
    accept(sock)


if __name__ == '__main__':
    main()
