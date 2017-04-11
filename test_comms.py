import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('35.2.135.78', 2000))
s.listen(1)
conn, addr = s.accept()
while 1:
    data = conn.recv(1024)
    if not data: break
    print data.split(',')
conn.close()