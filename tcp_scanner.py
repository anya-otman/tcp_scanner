import argparse
import socket
import sys
from threading import Thread, Lock
from queue import Queue

N_THREADS = 50
q = Queue()
print_lock = Lock()
host = ''


def scan_tcp_port(host: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, port))
    except socket.error:
        pass
    else:
        with print_lock:
            print('TCP port :', port, ' is open')
    finally:
        s.close()


def scan_thread():
    global q, host
    while True:
        # получаем номер порта из очереди
        port = q.get()
        # сканируем порт
        scan_tcp_port(host, port)
        # сообщаем очереди, что сканирование этого порта завершено
        q.task_done()


def main():
    global q, host

    parser = argparse.ArgumentParser(description='Сканер TCP портов',
                                     usage='[Адрес хоста] [Начало диапазона] [Конец диапазона]')
    parser.add_argument('host', type=str, help='Адрес хоста')
    parser.add_argument('start', type=int, help='Начальное значение диапазона')
    parser.add_argument('end', type=int, help='Конечное значение диапазона')
    args = parser.parse_args()

    host = args.host
    if args.start < 0 or args.end > 65535:
        sys.exit('Начало и конец диапазона должны быть в границах от 0 до 65535')
    else:
        for t in range(N_THREADS):
            t = Thread(target=scan_thread)
            t.daemon = True
            t.start()
        for port in range(args.start, args.end):
            q.put(port)
        q.join()


if __name__ == "__main__":
    main()
