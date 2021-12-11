import socket
import time


def auth():
    sock = socket.socket()
    sock.connect(("127.0.0.1", 9090))
    sock.recv(1024 * 16)
    sock.send("test".encode())
    sock.recv(1024 * 16)
    sock.send("test".encode())
    pwd = sock.recv(1024 * 16)
    main(sock, pwd)


def main(sock, pwd):
    tests = [("pwd", "\\"),
             ("ls", ""),
             ("mkdir 1", ""),
             ("touch 1", ""),
             ("cp 1.txt 1", ""),
             ("rm 1.txt", ""),
             ("cd 1", ""),
             ("mv 1.txt 2.txt", ""),
             ("write 2.txt qwerty", ""),
             ("cat 2.txt", "qwerty")]
    for index, test in enumerate(tests):
        request = test[0]
        sock.send(request.encode())
        time.sleep(0.1)
        res = sock.recv(1024).decode()
        response = "\n".join(res.split("\n")[:-1])
        print(f"Тест {index + 1}")
        print(f"Команда: {test[0]}")
        print(f"Ожидаемый результат: {test[1]}")
        print(f"Фактический результат: {response}")
        print(f"Тест прошел {'корректно' if response == test[1] else 'некорректно'}")
        print("*" * 50 + "\n")


if __name__ == '__main__':
    auth()
