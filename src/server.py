import socket

s = socket.socket()
host = socket.gethostname()
host = socket.gethostbyname(host)
port = 12345
print("Binding server to host: {}, port: {}".format(host, port))
s.bind((host, port))

s.listen(5)

while True:
    c, addr = s.accept()
    print("Got connection from ", addr)
    msg = "Thank you for connecting"
    c.send(msg.encode())
    c.close()
    s.close()
    break
