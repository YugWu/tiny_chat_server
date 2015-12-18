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
    '''
    Respone clients by default protocol.
    Parameter:
        fd_pool: list of file descriptor, maybe change this.
        clients: list of object of the class Client, maybe change this.
    Return:
        None.
    Default protocol:
        protocol - the first word of every message.
        send by client:
            0: show all clients information.
            1: sendto message to all clients.
            2: name this client by change client.name.
    '''
    for client in clients:
        if client.read_status == False:
            continue
        conn_fd = client.fd
        command = conn_fd.recv(1024)

        # End breaken fd
        if len(command) == 0:
            conn_fd.close()
            fd_pool.remove(conn_fd)
            clients.remove(client)
            continue

        # Get protocol word
        str_list = command.split(' ', 1)
        ptl = str_list[0]
        ptl = ptl[0]    #Delete '\n'
        print ptl
        # Respone command by protocol
        if ptl == '0':
            # Show client online
            name_list = []
            for clt in clients:
                name_list.append(clt.name + ' ')
            message = ''.join(name_list)
            conn_fd.sendall(message)
        elif ptl == '1':
            # Send message to all clients
            for clt in clients:
                if clt != client:   #Do not send to self
                    message = client.name + ' ' + str_list[-1]
                    clt.fd.sendall(message)
        elif ptl == '2':
            # Name client
            index = command.find(' ')
            # Delete '\n' in name
            client.name = command[index + 1:-1]
        else:
            conn_fd.sendall('2')

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

    # Wait for connected
    while True:
        ready_fds, [], [] = select.select(fd_pool, [], [])

        if listen_fd in ready_fds:
            conn_fd, addr = listen_fd.accept()

            client = Client()   #Add client information
            client.addr = addr
            client.fd = conn_fd
            # client.id = conn_fd.fileno()
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
