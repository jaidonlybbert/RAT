# Author: Jaidon Lybbert
# Date  : March 2021

"""Module handles communication hosted on HMI between RAT device and controls interface"""

import socket

def connection_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.0.0.116', 5007))
    return s

def main():
    controls_packet = b'cccc'
    s.sendall(controls_packet)
    sensor_data = s.recv(4)
    print(sensor_data)
    sys_status = s.recv(4)
    print(sys_status)

s = connection_init()

if __name__ == 'main':
    while(True):
        main()
