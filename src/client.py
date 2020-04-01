#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket

'''
This is a template that can be used in order to get started. 
It takes 3 commandline arguments and calls function send_and_receive_tcp.
in haapa7 you can execute this file with the command: 
python3 CourseWorkTemplate.py <ip> <port> <message> 

Functions send_and_receive_tcp contains some comments.
If you implement what the comments ask for you should be able to create 
a functioning TCP part of the course work with little hassle.  

''' 
 
def send_and_receive_tcp(address, port, message):

    print("\nAttempting to connect to TCP server.")
    print("Your inputs: {} {} {}".format(address, port, message))
    print("\nCreating TCP socket...")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(5)

    try:
        print("Connecting to {}:{}...".format(address, port))
        tcp_socket.connect((address, port))
        print("Sending message:", message)
        tcp_socket.send((message + "\r\n").encode())
        print("Receiving initial data...")
        data = tcp_socket.recv(4096).decode()
        print("Received data:")
        print(data)

        tcp_socket.close()

        # Get your CID and UDP port from the message
        udp_port = 11111

        # Continue to UDP messaging. You might want to give the function some other
        # parameters like the above mentioned cid and port.
        send_and_receive_udp(address, udp_port)

    except socket.gaierror:
        print("Invalid IP address specified.")
        tcp_socket.close()
        return
    return
 
 
def send_and_receive_udp(address, port):

    print("Attempting UDP communication.")
    print("Inputs: {}, {}".format(address, port))
    print("\nCreating UDP socket...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(5)
    msg = "HELLO from asd123\n"

    print("Sending message: {}".format(msg))
    udp_socket.sendto(msg.encode(), (address, port))
    data = udp_socket.recv(4096).decode()

    print("Receiving data...")
    print("Received:\n{}".format(data))

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
        # Print usage instructions and exit if we didn't get proper arguments
        sys.exit(USAGE)
    except ValueError:
        print("Value Error")
        # Print usage instructions and exit if we didn't get proper arguments
        sys.exit(USAGE)

    while True:
        user_input = menu()

        if user_input == "q":
            exit(0)
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
            try:
                send_and_receive_tcp(server_address, server_tcpport, message)
            except TimeoutError:
                print("Timeout Error")
            except socket.timeout:
                print("Server did not respond within timeout period. Exiting...")

 
if __name__ == '__main__':
    # Call the main function when this script is executed
    main()
