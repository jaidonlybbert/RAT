# Author: Jaidon Lybbert
# Date  : March 2021

"""Handles communication hosted on the RAT MCU between the RAT and the HMI"""

import socket
import utime

def connection_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('10.0.0.116', 5007))
    print("socket bound")
    s.listen(1)
    conn, addr = s.accept()
    return conn, addr, s


def recv_loop():
    while 1:
        controls_packet = conn.recv(2)
        print(controls_packet)

def main():
    controls_packet = conn.recv(4)    #expect 32 bit packet of control signals
    print(controls_packet)

    sensor_data = b'ssss' 
    sys_status = b'tttt' 

    time_before_send = utime.ticks_us()
    conn.send(sensor_data) #send back lidar data
    conn.send(sys_status)  #send system status
    print(utime.ticks_diff(utime.ticks_us(), time_before_send))

conn, addr, s = connection_init()

if __name__ == '__main__':
    while True:
        main()
