import os
import socket
import ssl
import base64


def main():
    hostname = 'smtp.yandex.ru'
    port = 465
    login = ''
    password = ''

    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            # Connect
            data = ssock.recv(1024).decode()
            if data[:3] != '220':
                print(f'Cannot connect to server: {data}')
                exit(1)

            # EHLO
            query = f'ehlo x\r\n'.encode()
            ssock.sendall(query)
            data = ssock.recv(1024).decode()
            if data[:3] != '250':
                print(f'Mail server is busy: {data}')
                exit(1)
            print(f'Connection to {hostname}:{port} established')

            # Login
            if not login:
                print('Type login')
                login = input()
            print(f'Login: {login}')
            if not password:
                print('Type password')
                password = input()
            print(f'Password: {password}')
            credentials = '\x00' + login + '\x00' + password
            credentials_base64 = base64.b64encode(credentials.encode())
            ssock.send('auth plain '.encode() +
                       credentials_base64 +
                       '\r\n'.encode())
            data = ssock.recv(1024).decode()
            if data[:3] != '235':
                print(f'Log in failed: {data}')
                exit(1)
            print('Logged in!')

            # New mail from you
            ssock.sendall(b'mail from: <' + login.encode() + b'>\r\n')
            data = ssock.recv(1024).decode()
            if data[:3] != '250':
                print(f'Sending not started: {data}')
                exit(1)

            # Commands
            print('Type email address (separated by space if multiple)')
            addresses = input()
            addresses.split()
            for a in addresses.split():
                ssock.sendall(b'rcpt to: <' + a.encode() + b'>\r\n')
                data = ssock.recv(1024).decode()
                if data[:3] != '250':
                    print(f'Setting for {a} failed: {data}')
                    exit(1)
                print(f'{a} - added')

            # Sending the mail
            query = f'data\r\n'.encode()
            ssock.sendall(query)
            data = ssock.recv(1024).decode()
            if data[:3] != '354':
                print(f'Mail server is not ready: {data}')
                exit(1)
            while True:
                print('Input path to .eml file')
                path = input()
                if not os.path.isfile(path):
                    print(f'{path} is not a file')
                else:
                    break
            with open(path, 'rb') as file:
                text = file.read()
                ssock.sendall(text + b'\r\n')
                ssock.sendall(b'.\r\n')

            data = ssock.recv(1024).decode()
            if data[:3] != '250':
                print(f'Not sent: {data}')
                exit(1)
            print(f'Mail {path} sent!')


if __name__ == '__main__':
    main()
