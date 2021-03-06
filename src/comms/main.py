# Author: Jaidon Lybbert
# Date  : March 2021

"""Handles communication hosted on the RAT MCU between the RAT and the HMI"""

import socket


def connection_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('10.0.0.116', 5007))
    s.listen(1)
    conn, addr = s.accept()


def main():
    while True:
        controls_packet = conn.recv(4)    #expect 32 bit packet of control signals
        print(data)

        sensor_data = sensor_data + 1
        sys_status = sys_status * 2

        conn.send(sensor_data) #send back lidar data
        conn.send(sys_status)  #send system status


connection_init()

if __name__ == "main":
    main()
