import socket
import threading

def scan_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((target, port))
    if result == 0:
        print(f'[+] port {port} is open')
    sock.close()

def main(target, ports):
    threads = []
    for port in ports:
        thread = threading.Thread(target=scan_port, args=(target, port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    target = '192.168.40.246'
    ports = range(20,1000)
    main(target, ports)

