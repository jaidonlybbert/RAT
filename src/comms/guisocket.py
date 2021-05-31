# Author: Jaidon Lybbert
# Date  : March 2021

"""Module handles communication hosted on HMI between RAT device and controls interface"""

import socket
import time

def connection_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_timeout = time.time() + 20

    while(conn_timeout - time.time() > 0):
        try:
            s.connect(('10.0.0.116', 5007))
            print('Successfully connected')
            return s
        except ConnectionError:
            print('No connection. Attempting reconnection. Reset peer.')
            time.sleep(1)
    
    print('Connection timed out.')
    return


def read_ctrl_inputs():
    return b'ctrl'


def parse_recv_data(sensor_data, sys_status):
    print(sensor_data)
    print(sys_status)    


def main():
    s.send(read_ctrl_inputs())
    parse_recv_data(s.recv(4), s.recv(4))


if __name__ == '__main__':
    s = connection.init()
    if s: 
        while(True):
            main()
