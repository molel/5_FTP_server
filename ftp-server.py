import shutil
import socket
import os
import os.path
import Auth
from datetime import datetime

LOG = "server_log.txt"
AUTH = "auth.json"
LOGIN = "Введите логин"
PASSWORD = "Введите пароль"
NEW_PASSWORD = "Задайте пароль"
SUCCESS = "Вход выполнен"
EXIT = "exit\n"
PORT = 6666
ENCODING = "UTF-8"
HOME = ""


def ls(path=HOME):
    return "\n".join(os.listdir(path))


def pwd():
    return os.getcwd()


def mkdir(dirname):
    os.mkdir(dirname)


def rmdir(dirname):
    shutil.rmtree(dirname)


def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


# получение данных об аутентификации
def read_auth(filename: str) -> dict:
    with open(filename, "r") as file:
        auth: dict = dict()
        for row in file:
            try:
                login: str = row.split(":")[0]
                password: str = row.split(":")[1][:-1]
                auth[login] = password
            except:
                pass
        else:
            return auth


# добавление данных аутентификации
def add_auth(filename: str, login: str, password: str):
    with open(filename, "a") as file:
        file.write(f"{login}:{password}\n")


# функция добавления новой записи в файл логов
def write_log(filename: str, log: str):
    with open(filename, "a") as file:
        file.write(f"{datetime.now()}:\n{log}\n\n")


def bind(sock: socket.socket, port: int = 9090):
    try:
        sock.bind(("127.0.0.1", port))
        write_log(LOG, f"Сервер привязан к 127.0.0.1, {port}")
    except:
        bind(sock, port + 1)


def auth(sock: socket.socket, conn: socket.socket, addr: str):
    login = get_login(conn)
    write_log(LOG, f"Получено '{login}'")
    if login in users.keys():
        get_password(sock, conn, addr, users[login])
    else:
        get_new_password(sock, conn, addr, login)


def get_login(conn: socket.socket) -> str:
    conn.send(LOGIN.encode())
    write_log(LOG, f"Отправлено '{LOGIN}'")
    return conn.recv(2048).decode()


def get_password(sock: socket.socket, conn: socket.socket, addr: str, correct_password: str):
    conn.send(PASSWORD.encode())
    write_log(LOG, f"Отправлено '{PASSWORD}'")
    password = conn.recv(2048).decode()
    write_log(LOG, f"Получено '{password}'")
    if correct_password == password:
        echo(sock, conn, addr)
    else:
        get_password(sock, conn, addr, correct_password)


def get_new_password(sock: socket.socket, conn: socket.socket, addr: str, login: str):
    global users
    conn.send(NEW_PASSWORD.encode())
    write_log(LOG, f"Отправлено '{NEW_PASSWORD}'")
    new_password = conn.recv(2048).decode()
    write_log(LOG, f"Получено '{new_password}'")
    add_auth(AUTH, login, new_password)
    echo(sock, conn, addr)


def process(request: str) -> str:
    command, *args = request.split(" ")
    try:
        return COMMANDS[command](*args)
    except:
        return "incorrect request"


def echo(sock: socket.socket, conn: socket.socket, addr: str):
    conn.send(SUCCESS.encode())
    write_log(LOG, f"Отправлено '{SUCCESS}'")
    while True:
        try:
            request = conn.recv(2048)
            write_log(LOG, f"Получено '{request.decode()}'")
            response: str = process(request)
            if request.decode() == EXIT:
                users.set_field_value(addr, "is_logged_in", False)
                accept(sock)
            else:
                conn.send(request)
                write_log(LOG, f"Отправлено '{request.decode()}'")
        except:
            accept(sock)
            break


def accept(sock: socket.socket):
    while True:
        try:
            conn, (addr, port) = sock.accept()
            write_log(LOG, f"Соединено с {addr}, {port}")
            auth(sock, conn, addr)
            break
        except:
            continue


COMMANDS = {
    "ls": ls,
    "pwd": pwd,
    "mkdir": mkdir,
    "rm": rm,
    "cpc2s": cpc2s,
    "cps2c": cps2c,
    "exit": exit_,
    "help": help_
}
users = Auth.read_auth(AUTH)


def main():
    sock: socket.socket = socket.socket()
    bind(sock)
    sock.listen(1)
    accept(sock)


if __name__ == '__main__':
    main()
