import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('35.2.135.78', 2000))
s.listen(1)
conn, addr = s.accept()
while 1:
    data = conn.recv(1024)
    if not data: break
    speed = data.split(',')[0]
    angle = data.split(',')[1]
    print 'Speed=' + str(speed)
    print 'Angle=' + str(angle)
conn.close()