import shutil

from server import writeLog, send, recv
from settings import *


class FileManager:

    def __init__(self, sock, conn, login):
        self.socket = sock
        self.connection = conn
        self.login = login
        self.root = os.getcwd()
        if login == ADMIN:
            os.chdir(WORKING_DIRECTORY)
            self.root = WORKING_DIRECTORY
            self.login = "#" + self.login
        self.currentPath = self.root

    def dirSize(self, path_):
        size = 0
        for path, dirs, files in os.walk(path_):
            for dir_ in dirs:
                size += self.dirSize(os.path.join(path, dir_))
            for file in files:
                size += os.path.getsize(os.path.join(path, file))
        return size

    def checkPath(self, path):
        return self.root in os.path.abspath(path)

    def pwd(self):
        path = os.getcwd().replace(self.root, "")
        if path == "":
            path = "\\"
        return path + "\n"

    def ls(self):
        return "\n".join(os.listdir(self.currentPath)) + "\n"

    def cd(self, path):
        if path == "~":
            path = self.root
        if self.checkPath(path) and os.path.isdir(path):
            os.chdir(path)
            self.currentPath = os.path.join(self.currentPath, path)
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def mkdir(self, path):
        if self.checkPath(path):
            os.mkdir(path)
            if self.dirSize(self.root) > MAX_DIRECTORY_SIZE:
                self.rm(path)
                return LACK_OF_MEMORY + "\n"
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def mv(self, source, destination):
        if self.checkPath(source) and self.checkPath(destination) and os.path.exists(os.path.abspath(source)):
            shutil.move(source, destination)
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def rm(self, path):
        if self.checkPath(path) and os.path.exists(os.path.abspath(path)):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def cat(self, path):
        if self.checkPath(path) and os.path.exists(os.path.abspath(path)):
            return open(path, "r", encoding=ENCODING).read() + "\n"
        else:
            return INCORRECT_PATH + "\n"

    def touch(self, path):
        if self.checkPath(path):
            if not path.endswith(".txt"):
                path += ".txt"
            open(path, "a", encoding=ENCODING).close()
            if self.dirSize(self.root) > MAX_DIRECTORY_SIZE:
                self.rm(path)
                return LACK_OF_MEMORY + "\n"
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def write(self, *args):
        path, text = args[0], " ".join(args[1:])
        if self.checkPath(path) and os.path.isfile(path):
            tempText = open(path, "r", encoding=ENCODING).read()
            open(path, "a", encoding=ENCODING).write(text)
            if self.dirSize(self.root) > MAX_DIRECTORY_SIZE:
                with open(path, "w", encoding=ENCODING) as file:
                    file.write(tempText.replace(text, "", (tempText.count(text) - 1)))
                    return LACK_OF_MEMORY + "\n"
            return "\n"
        else:
            return INCORRECT_PATH + "\n"

    def free(self):
        return f"Всего места: {MAX_DIRECTORY_SIZE}\nСвободно: {MAX_DIRECTORY_SIZE - self.dirSize(self.root)}\n"

    @staticmethod
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
               "free - выводит информацию о памяти" \
               "exit - разрыв соединения с сервером\n" \
               "help - выводит справку по командам\n"

    def process(self, request):
        command, *args = request.split(" ")

        writeLog(LOG, f"От пользователя {self.root} получено '{request}'")

        try:
            response = self.COMMANDS[command](self, *args)
        except:
            response = "incorrect request\n"

        writeLog(LOG, f"Пользователю {self.root} отправлено '{response}'")

        return response

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
        "free": free,
        "help": help_
    }


def handle(sock, conn, login):
    checkDirectory(login)
    fileManager = FileManager(sock, conn, login)
    send(conn, CORRECT_PASSWORD + "\n" + fileManager.login + "$" + fileManager.pwd()[:-1] + ">")
    writeLog(LOG, f"Пользователь {fileManager.login} авторизовался")
    while True:
        try:
            request = recv(conn)
            if request == "exit":
                conn.close()
            response = fileManager.process(request)
            send(conn, response)
            send(conn, fileManager.login + "$" + fileManager.pwd()[:-1] + ">")
        except:
            break

    os.chdir(WORKING_DIRECTORY)
    conn.close()


def checkDirectory(login):
    login = WORKING_DIRECTORY + SEP + login
    if not os.path.exists(login) or not os.path.isdir(login):
        os.mkdir(login)
    os.chdir(login)
