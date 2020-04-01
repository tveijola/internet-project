import socketserver


class UDPConnectionHandler(socketserver.BaseRequestHandler):
    def handle(self):

        word_list1 = "uno dos tres quatro"
        word_list2 = "saippua kivi perkele kauppias"

        data = self.request[0].decode()
        sock = self.request[1]
        print("Received UDP message from {}:".format(self.client_address[0]))
        print(data)
        print("Sending response...")
        sock.sendto(word_list1.encode(), self.client_address)


class TCPConnectionHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(4096).decode()
        print("Received TCP message from {}:".format(self.client_address[0]))
        print(data)
        print("Sending response...")

        self.request.sendall("HELLO asd123 11111\r\n".encode())

        udp_host, udp_port = "localhost", 11111
        udp_server = socketserver.UDPServer((udp_host, udp_port), UDPConnectionHandler)
        udp_server.timeout = 2
        udp_server.handle_request()

        print("Listening...")


if __name__ == "__main__":
    print("Starting server...")
    print("Address: localhost")
    print("Port: 12345")
    HOST, PORT = "localhost", 12345
    tcp_server = socketserver.TCPServer((HOST, PORT), TCPConnectionHandler)
    print("\nListening...")
    tcp_server.serve_forever()
