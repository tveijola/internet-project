#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
import struct
import random

'''
This is a template that can be used in order to get started. 
It takes 3 commandline arguments and calls function send_and_receive_tcp.
in haapa7 you can execute this file with the command: 
python3 CourseWorkTemplate.py <ip> <port> <message> 

Functions send_and_receive_tcp contains some comments.
If you implement what the comments ask for you should be able to create 
a functioning TCP part of the course work with little hassle.  

'''

HEXCHARS = '0123456789abcdefABCDEF'

def generate_key():
    return "".join(random.choice(HEXCHARS) for i in range(64))

def send_and_receive_tcp(address, port, message):

    print("\nCreating TCP socket.")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("Connecting to {}:{}...".format(address, port))
        tcp_socket.connect((address, port))
        
        message = message + " ENC MUL PAR\r\n"
        client_keys = []
        for i in range(20):
            key = generate_key()
            client_keys.append(key)
            message = message + key + "\r\n"
        message = message + ".\r\n"

        print("Sending initial message...\n")
        tcp_socket.send((message + "\r\n").encode())
        
        print("Receiving data...")
        data = tcp_socket.recv(4096)
        msg = data.decode()
        print("Received data:", msg.strip())
        
        # Get your CID and UDP port from the message
        data_list = msg.split()
        cid = data_list[1]
        udp_port = int(data_list[2])
        server_keys = []
        for i in range(20):
            key = data_list[i+3]
            server_keys.append(key.strip())

        tcp_socket.close()
        send_and_receive_udp(address, udp_port, cid, client_keys, server_keys)

    except socket.gaierror:
        print("Invalid IP address specified.")
        tcp_socket.close()
        return
    return


def crypt(text, key):
    return "".join(chr(ord(text[i]) ^ ord(key[i])) for i in range(len(text)))

def pieces(msg, length=64):
    parts = []
    start, end = 0, length
    next_part = msg[start:end]
    while next_part:
        start, end = start+length, end+length
        parts.append(next_part)
        next_part = msg[start:end]
    return parts

def get_parity(n):
    while n > 1:
        n = (n >> 1) ^ (n & 1)
    return n

def add_parity(msg):
    char_list = []
    for c in msg:
        c = ord(c)
        c <<= 1
        c += get_parity(c)
        char_list.append(chr(c))
    return "".join(char_list)

def check_parity(msg):
    char_list = []
    parity = True
    for c in msg:
        num = ord(c)
        if parity:
            char_parity = bin(num).count('1') % 2 == 0
            if not char_parity:
                parity = False
        char_list.append(chr(num >> 1))
    return "".join(char_list), parity

def send_and_receive_udp(address, port, cid, client_keys, server_keys):

    print("\nCreating UDP socket...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(5)
    msg = "Hello from " + cid
    cid = cid.encode()
    packet_format = '!8s??HH128s'

    print("Sending initial message")
    if client_keys:
        msg = crypt(msg, client_keys.pop(0))
    msg, eom = add_parity(msg), False
    packet = struct.pack(packet_format, cid, True, eom, 0, len(msg), msg.encode())
    udp_socket.sendto(packet, (address, port))

    while not eom:
        # Receive message
        data_remaining, content, parity_ok = 1, "", True
        while data_remaining != 0:
            data = udp_socket.recv(1024)
            _, ack, eom, data_remaining, content_len, next_part = struct.unpack(packet_format, data)
            next_part = next_part.decode()[0:content_len]
            if eom:
                print("\nReceived:", next_part.strip())
                break
            next_part, parity = check_parity(next_part)
            if not parity:
                parity_ok = False
            if server_keys:
                next_part = crypt(next_part, server_keys.pop(0))
            content += next_part
        # If not the last message, send reply
        if not eom:
            # If parity check is OK, send normal reply
            if parity_ok:
                print("Received:", content.strip())
                word_list = content.split()
                word_list.reverse()
                msg = " ".join(word_list)
                print("Reversed: {}\n".format(msg.strip()))
            # If error in parity, request resend
            elif not parity_ok:
                print("ERROR IN PARITY DETECTED! Message: {}\n".format(content.strip()))
                msg = "Send again"
            # Split msg to 64 byte parts and send each piece
            parts, remaining = pieces(msg), len(msg)
            for part in parts:
                remaining -= len(part)
                if client_keys:
                    part = crypt(part, client_keys.pop(0))
                part = add_parity(part)
                packet = struct.pack(packet_format, cid, parity_ok, False, remaining, len(part), part.encode())
                udp_socket.sendto(packet, (address, port))
    return


def menu():
    print("\n----- CLIENT PROGRAM -----")
    print("Specify your selection by inputting a single number or character and press enter.")
    print("1 - Print current connection settings.")
    print("2 - Modify server address.")
    print("3 - Modify server port.")
    print("4 - Connect to server")
    print("q - quit")
    return input("> ")

def getNewAddress():
    return input("Input server Address:\n> ")

def getNewPort():
    return input("Input server Port:\n> ")

def main():

    USAGE = 'usage: %s <server address> <server port> <message>' % sys.argv[0]

    try:
        # Get the server address, port and message from command line arguments
        server_address = str(sys.argv[1])
        server_tcpport = int(sys.argv[2])
        message = str(sys.argv[3])
    except IndexError:
        print("Index Error")
        exit(USAGE)
    except ValueError:
        print("Value Error")
        exit(USAGE)

    while True:
        user_input = menu()
        if user_input == "q":
            exit()
        elif user_input == "1":
            print("\nCurrent settings:")
            print("Address: ", server_address)
            print("Port: ", server_tcpport)
        elif user_input == "2":
            server_address = getNewAddress()
        elif user_input == "3":
            try:
                server_tcpport = int(getNewPort())
            except ValueError:
                print("\n----- ERROR -----")
                print("The tcp port must be an integer!")

        elif user_input == "4":
            # Proceed with TCP communication
            try:
                send_and_receive_tcp(server_address, server_tcpport, message)
            except TimeoutError:
                print("Timeout Error")
            except socket.timeout:
                print("Server did not respond within timeout period.")


if __name__ == '__main__':
    # Call the main function when this script is executed
    main()