#!/usr/bin/python
'''A tiny server for chat'''
import socket
import select

def open_listed_fd(port):
    '''Open a listen socket'''
    listen_fd = (
        socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    listen_fd.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_fd.bind(('', port))
    listen_fd.listen(10)
    return listen_fd

def respone_clients(fd_pool, clients):
    '''Respone clients'''
    for client in clients:
        if client.read_status == False:
            continue
        conn_fd = client.fd
        command = conn_fd.recv(1024)

        # End breaken fd
        if len(command) == 0:
            fd_pool.remove(conn_fd)
            clients.remove(client)
            continue
        # Echo
        print command

        # Respone command request
        if 'show' in command:
            # Show client online
            conn_fd.sendall(''.join(clt.name
                            + ' ' + str(clt.id) + '\n' for clt in clients))
        elif 'sendto' in command:
            # Send message to a client by id
            str_list = command.split(' ', 2)
            try:
                clt_id = int(str_list[1])
            except ValueError:
                conn_fd.sendall('Wrong id!')
                continue
            for clt in clients:
                if clt_id == clt.id:
                    message = str(client.id) + ' ' + str_list[-1]
                    clt.fd.send(message)
                    continue
        elif 'name' in command:
            # Set client name
            index = command.find(' ')
            # Delete '\n' in name
            client.name = command[index + 1:-1]
        else:
            conn_fd.sendall('Wrong command!')

        client.read_status = False

class Client():
    """docstring for Client"""
    def __init__(self):
        self.fd = None
        self.name = 'Uname'
        self.id = -1
        self.addr = ''
        self.read_status = False

def main():
    '''Main'''
    # Init socket pool and client pool
    fd_pool = []
    clients = []

    listen_fd = open_listed_fd(2233)
    fd_pool.append(listen_fd)

    # Start respone by thread
    # thread.start_new_thread(respone_massage, ())
    # Wait for connected
    while True:
        ready_fds, [], [] = select.select(fd_pool, [], [])

        if listen_fd in ready_fds:
            conn_fd, addr = listen_fd.accept()

            client = Client()
            client.addr = addr
            client.fd = conn_fd
            client.id = conn_fd.fileno()
            clients.append(client)

            print 'connect', addr
            fd_pool.append(conn_fd)

            # Delete listen_fd
            ready_fds.remove(listen_fd)

        for client in clients:
            if client.fd in ready_fds:
                client.read_status = True

        # Respone each connected client in pool
        respone_clients(fd_pool, clients)

if __name__ == '__main__':
    main()
