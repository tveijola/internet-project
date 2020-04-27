#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
import struct
import random

HEXCHARS = '0123456789abcdefABCDEF'

def generate_key(key_len=64):
    # Generate encryption keys of hexadecimal characters of lenght [key_len]
    return "".join(random.choice(HEXCHARS) for i in range(key_len))

def crypt(text, key):
    # Perform XOR between [text] and [key]
    return ''.join(chr(ord(text[i]) ^ ord(key[i])) for i in range(len(text)))

def pieces(msg, piece_size=64):
    # Returns the input string as a list of strings of length [piece_size]
    return [msg[i:i+piece_size] for i in range(0, len(msg), piece_size)]

def get_parity(c):
    # Returns 1 if input character c binary form contains an odd number of 1's, 0 otherwise
    n = ord(c)
    while n > 1:
        n = (n >> 1) ^ (n & 1)
    return n

def add_parity(msg):
    # Adds parity bits to chars in input string and returns the modified string
    return ''.join(chr((ord(c) << 1) + get_parity(c)) for c in msg)

def check_parity(msg):
    # Checks input string characters for parity
    # Returns the input string without parity bits and the boolean parity value
    parity = all(get_parity(c) == 0 for c in msg)
    msg = ''.join(chr(ord(c) >> 1) for c in msg)
    return msg, parity

def menu():
    # Shows alternatives for the user
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

def send_and_receive_tcp(address, port, msg):

    print("\nCreating TCP socket.")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("Connecting to {}:{}...".format(address, port))
        tcp_socket.connect((address, port))

        # Generate encryption keys and add to msg
        client_keys = [generate_key() for i in range(20)]
        keys_text = "".join(key + "\r\n" for key in client_keys)
        msg += " ENC MUL PAR\r\n" + keys_text + ".\r\n"

        print("Sending initial HELLO message...\n")
        tcp_socket.send(msg.encode())
        print("Receiving data...")
        data = tcp_socket.recv(4096).decode()
        print("Received data:", data.strip())
        tcp_socket.close()
        
        # Get your CID and UDP port from the message
        data_list = data.split()
        cid = data_list[1]
        udp_port = int(data_list[2])
        server_keys = [data_list[i].strip() for i in range(3, 23)]

        # Proceed to UPD communication
        send_and_receive_udp(address, udp_port, cid, client_keys, server_keys)

    except socket.gaierror:
        print("Invalid IP address specified.")
        return
    except ConnectionRefusedError:
        print("Destination address machine refused the connection. Server is possibly down.")
    finally:
        tcp_socket.close()
    return

def send_and_receive_udp(address, port, cid, client_keys, server_keys):

    print("\nCreating UDP socket...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = "Hello from " + cid
    cid, packet_format = cid.encode(), '!8s??HH128s'
    parity_ok, eom = True, False
    print("Sending initial message\n")

    while not eom:
        # Split msg to 64 byte parts and send each piece
        parts, remaining = pieces(msg), len(msg)
        for part in parts:
            print("Sending PART:", part)
            remaining -= len(part)
            if client_keys:
                part = crypt(part, client_keys.pop(0))
            part = add_parity(part)
            packet = struct.pack(packet_format, cid, parity_ok, False, remaining, len(part), part.encode())
            udp_socket.sendto(packet, (address, port))

        # Receive next message
        data_remaining, content, parity_ok = 1, "", True
        while data_remaining != 0:
            data = udp_socket.recv(4096)
            _, ack, eom, data_remaining, content_len, next_part = struct.unpack(packet_format, data)
            next_part = next_part.decode()[0:content_len]
            if eom:
                print("\nReceived:", next_part.strip())
                return
            next_part, parity = check_parity(next_part)
            if not parity:
                parity_ok = False
            if server_keys:
                next_part = crypt(next_part, server_keys.pop(0))
            print("NEXTPART:", next_part)
            content += next_part

        # Generate reply
        if parity_ok:
            print("Received:", content.strip())
            word_list = content.split()
            word_list.reverse()
            msg = " ".join(word_list)
            print("Reversed: {}\n".format(msg.strip()))
        elif not parity_ok:
            print("ERROR IN PARITY DETECTED! Message: {}\n".format(content.strip()))
            msg = "Send again"
    return

def main():
    """
    key = generate_key()
    text = "This text needs to be sent."
    print(text)
    encrypted = crypt(text, key)
    print(encrypted)
    encrypted_parity_added = add_parity(encrypted)
    print(encrypted_parity_added)
    encrypted_parity_checked, par = check_parity(encrypted_parity_added)
    print(encrypted_parity_checked, par)
    decrypted = crypt(encrypted_parity_checked, key)
    print(decrypted)
    return
"""

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