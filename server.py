#!/usr/bin/env python2
import socket
import struct
import sys
import time


class Config(object):
    
    """
    Configuration settings.

    Various constants used for the adhoc server connection.

    Steps to a valid and stable connection:
    1. Login Packet
    2. Ping Packet
    3. Network Scan Packet
    4. Ping Packet
    TODO: Figure out the rest
    """

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
    try:
        connection, client_address = sock.accept()
        # TODO: Validate this connection
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
                # Add the user to the connection
                if macaddress in Config.USERS:
                    print "Mac Address is already connected."
                    print "If using ppsspp try using a different MAC."
                else:
                    # All went good, let the admin know about the connection
                    print "{} (MAC: {} - IP: {}) started playing {}.".format(username, macaddress, client_address[0], productcode)
                    # Add the user to the list
                    Config.USERS[macaddress] = {'nickname': username, 
                    'product': productcode, 'ipaddress': client_address[0],
                    'socket': connection, 'timeout': int(time.time())}
            # FIXME: Read in next 10 packets; Debug style (yuck)
            for i in range(0, 10):
                for macaddress in Config.USERS:
                    # TODO: Add a check to make sure the user logs in before doing this logic
                    # TODO: Cycle for each connected user
                    user = Config.USERS[macaddress]
                    packet = user['socket'].recv(1024)
                    if len(packet) > 0:
                        # TODO: Update the timeout clock for the connected user.
                        # Extract the packet opcode
                        opcode = struct.unpack('!B', packet[0])[0]
                        if opcode == Config.PACKET_PING:
                            print "Ping Packet"
                            # Update the timeout timer
                            user['timeout'] = int(time.time())
                        elif opcode == Config.PACKET_CONNECT:
                            # TODO: Check for Group Connect packet
                            print "Group Connect Packet"  
                        elif opcode == Config.PACKET_DISCONNECT: 
                            print "Group Disconnect Packet"
                        elif opcode == Config.PACKET_SCAN:
                            print "Network Scan Packet"
                            # Throw away packet
                            # TODO: Send network list
                            # 1. Is this user in a group?
                            # if no then:
                            # Create a new packet with opcode scan
                            # else:

                            # Send packet a PACKET_SCAN_COMPLETE
                        elif opcode == Config.PACKET_CHAT:
                            print "Text Chat Packet"
                        else:
                            print "Invalid Packet opcode: {}".format(opcode)
                            break
                    else:
                        # TODO: We received a disconnect or something went wrong.
                        # TODO: Log out the user.
                        print "Error occurred while receiving the packet."
                        break
    finally:
        connection.close()

if __name__ == "__main__":
    sys.exit(main())
