import os
import os.path
import shutil
from tkinter import *
from tkinter.font import Font
from tkinter.messagebox import showerror
from zipfile import ZipFile
from json import load


class FileManager:
    SETTINGS: str = "settings.json"

    def __init__(self, user_dir: str):
        self.commands: dict = {


        }
        self.root: str = self.set_root(user_dir)  # текущий путь
        self.path: str = ""  # видимый для пользователя путь

    # установка корневого каталога
    def set_root(self, user_dir: str):
        with open(FileManager.SETTINGS, "r") as settings:
            root_dir: str = load(settings)["directory"].replace("\\", "\\\\")
        if not os.path.exists(root_dir):
            self.mkdir(root_dir)
        if not os.path.exists(root_dir + os.sep + user_dir):
            self.mkdir(root_dir + os.sep + user_dir)
        os.chdir(root_dir + os.sep + user_dir)
        return os.getcwd()


    # отображение каталогов и файлов в текущем каталоге
    def display_dir_content(self):
        self.file_list.delete(0, END)
        for file in os.listdir(os.getcwd()):
            self.file_list.insert(END, file)

    # отображение текущего пути
    def display_path(self):
        self.text.set(self.path)

    # отображение содержимого файла
    def display_content(self, content: list):
        self.file_content.delete(0, END)
        for line in content:
            self.file_content.insert(END, line)

    # считывание и выполнение команды из поля ввода
    def get_command(self, event: Event):
        line = self.console.get().split(" ")
        self.console.delete(0, END)
        if len(line) > 0:
            command, arguments = line[0], line[1:]
            if command in self.commands.keys():
                self.commands[command](*arguments)
            else:
                showerror("Warning", "There is no such command")
            self.display_path()

    # создание нового каталога
    def mkdir(self, *args):
        if len(args) > 1:
            showerror("Warning", "Too many arguments")
        else:
            dirName: str = args[0]
            try:
                os.mkdir(os.getcwd() + os.sep + dirName)
                self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])

    # удаление каталога
    def rmdir(self, *args):
        if len(args) > 1:
            showerror("Warning", "Too many arguments")
        else:
            dirName: str = args[0]
            try:
                shutil.rmtree(os.getcwd() + os.sep + dirName)
                self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])

    # изменение текущего каталога
    def cd(self, *args):
        if len(args) > 1:
            showerror("Warning", "Too many arguments")
        else:
            try:
                temp_path: str = os.getcwd()
                os.chdir(args[0])
                if self.root not in os.getcwd():
                    showerror("Warning", "Указан некорректный путь")
                    os.chdir(temp_path)
                else:
                    self.path = os.getcwd().replace(self.root, "")
                    self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])

    # создание пустых текстовых файлов
    def touch(self, *args):
        try:
            for file_name in args:
                if ".txt" not in file_name:
                    file_name += ".txt"
                open(file_name, 'a').close()
            self.display_dir_content()
        except Exception as e:
            showerror("Warning", e.args[1])

    # дозапись в текстовый файл
    def echo(self, *args):
        if len(args) < 2:
            showerror("Warning", "Too few arguments")
        else:
            try:
                file_name: str = args[0]
                data: tuple = args[1:]
                with open(file_name, 'a') as file:
                    file.write(" ".join(data) + "\n")
                self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])

    # вывод содержимого файла
    def cat(self, *args):
        if len(args) > 1:
            showerror("Warning", "Too many arguments")
        else:
            try:
                file_name = args[0]
                with open(file_name, 'r') as file:
                    self.display_content(file.readlines())
            except Exception as e:
                showerror("Warning", e.args[1])

    # удаление файлов
    def rm(self, *file_names):
        try:
            for file_name in file_names:
                os.remove(file_name)
            self.display_dir_content()
        except Exception as e:
            showerror("Warning", e.args[1])

    # копирование файлов
    def cp(self, *args):
        file_names: tuple = args[:-1]
        dirPath: str = args[-1]
        try:
            for file_name in file_names:
                shutil.copy(file_name, dirPath)
            self.display_dir_content()
        except Exception as e:
            showerror("Warning", e.args[1])

    # перемещение файлов
    def mv(self, *args):
        file_names: tuple = args[:-1]
        dirPath: str = args[-1]
        for file_name in file_names:
            shutil.move(file_name, dirPath)

        self.display_dir_content()

    # переименование файлов
    def rename_file(self, *args):
        if len(args) > 2:
            showerror("Warning", "Too many arguments")
        elif len(args) < 2:
            showerror("Warning", "Too few arguments")
        else:
            file_name: str = args[0]
            new_file_name: str = args[1]
            if ".txt" not in new_file_name:
                new_file_name += ".txt"
            os.rename(file_name, new_file_name)
        self.display_dir_content()

    def archive(self, *args):
        if len(args) < 1:
            showerror("Warning", "Too few arguments")
        else:
            try:
                with ZipFile(args[0].split(".")[0] + ".zip", "w") as zip_file:
                    for file_name in args:
                        zip_file.write(file_name)
                    self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])

    def extract(self, *args):
        if len(args) > 1:
            showerror("Warning", "Too many arguments")
        else:
            try:
                with ZipFile(args[0]) as zip_file:
                    self.mkdir(args[0].replace(".zip", ""))
                    zip_file.extractall(args[0].replace(".zip", ""))
                    self.display_dir_content()
            except Exception as e:
                showerror("Warning", e.args[1])
