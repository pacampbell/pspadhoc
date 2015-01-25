#!/usr/bin/env python2
import socket
import struct
import sys


class Config(object):
    PORT = 27312
    # Packet Types
    PACKET_PING = 0x0
    PACKET_LOGIN = 0x1
    PACKET_CONNECT = 0x2
    PACKET_DISCONNECT = 0x3
    PACKET_SCAN = 0x4
    PACKET_SCAN_COMPLETE = 0x5
    PACKET_CONNECT_BSSID = 0x6
    PACKET_CHAT = 0x7
    # Packet Sizes in bytes
    PACKET_SIZE_LOGIN = 144
    # Product Code
    PRODUCT_CODE_LENGTH = 9
    # AdHoc UserName
    ADHOC_USERNAME_LENGTH = 128
    # The devices mac address should be used as the key
    USERS = {}


def main():
    # Create a TCP/IP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a port
    server_address = ('localhost', Config.PORT)
    sock.bind(server_address)
    # Now wait and listen for incomming calls
    sock.listen(1)
    # Wait for a connection
    print "Waiting for a connection on port {}".format(Config.PORT)
    connection, client_address = sock.accept()
    try:
        # TODO: Validate this connection
        print "New connection from {}".format(client_address)
        packet = connection.recv(1024)
        # TODO: Check for closed connection/timeout/interrupt
        packet_size = len(packet)
        if packet_size > 0:
            # TODO: Update the time for the user last update (for timeout)
            print "Received {} bytes.".format(packet_size)
            # Check the opcode
            opcode = struct.unpack('!B', packet[0])[0]
            # Handle a packet of login type
            if opcode == Config.PACKET_LOGIN and packet_size == Config.PACKET_SIZE_LOGIN:
                print "Received a Login Packet"
                """
                LOGIN Packet - 145 bytes
                +-----------+----------------+
                | [0,1)     | OPCODE: 0x01   |
                +-----------+----------------+
                | [1,7)     | mac address    |
                +-----------+----------------+
                | [7,135)   | adhoc username |
                +-----------+----------------+
                | [135,144) | Product Code   |
                +-----------+----------------+
                """
                # Extract The mac Address; There must be a cleaner way?
                raw_macaddress = struct.unpack('!6s', packet[1:7])[0]
                macaddress = ""
                for i in range(0, len(raw_macaddress)):
                    macaddress = "{}{:02x}:".format(macaddress, ord(raw_macaddress[i]))
                # Slice off the last ':'
                macaddress = macaddress[0: -1]
                # Extract the usernmae
                raw_username = struct.unpack('!128s', packet[7:135])[0]
                # Find the correct username in the field
                i = 0
                username = "" 
                while i < 128 and raw_username[i] >= 'A' and raw_username[i] <= 'z':
                    username = "{}{}".format(username, raw_username[i])
                    i = i + 1;
                # Extract the Product Code
                productcode = struct.unpack('!9s', packet[135:144])[0]
                # All went good, let the admin know about the connection
                print "{} (MAC: {} - IP: {}) started playing {}.".format(username, macaddress, client_address[0], productcode)
    finally:
        connection.close()

if __name__ == "__main__":
    sys.exit(main())
