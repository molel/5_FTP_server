# from FileManager import FileManager
# 
# 
# class Auth:
#     AUTH: str = "auth.txt"  # файл аутентификации
# 
#     def __init__(self, conn, login, password):
#         self.conn = conn
#         self.login = login
#         self.password = password
#         self.logins = read_auth(Auth.AUTH)  # данные аутентификации
# 
#     # проверка логина и пароля
#     def auth(self):
#         if self.login in self.logins.keys():
#             if self.password == self.logins[self.login]:
#                 FileManager(self.login)
#             else:
#                 return "incorrect login"
#         else:
#             add_auth(Auth.AUTH, self.login, self.password)
#             return f"user {self.login} was registered"


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
