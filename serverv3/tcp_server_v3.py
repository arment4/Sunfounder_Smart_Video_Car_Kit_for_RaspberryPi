#!/usr/bin/env python
import RPi.GPIO as GPIO
import video_dir
import car_dir
import motor
import csv
import datetime
import cv2
from socket import *
from time import ctime          # Import necessary modules

ctrl_cmd = ['forward', 'backward', 'left', 'right', 'stop', 'read cpu_temp',
    'home', 'distance', 'x+', 'x-', 'y+', 'y-', 'xy_home', 'quit']

busnum = 1          # Edit busnum to 0, if you uses Raspberry Pi 1 or 0

# The variable of HOST is null, so the function bind( ) can be bound to all valid addresses.
HOST = ''
PORT = 21567
BUFSIZ = 1024       # Size of the buffer
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)    # Create a socket.
tcpSerSock.bind(ADDR)    # Bind the IP address and port number of the server.
# The parameter of listen() defines the number of connections permitted at one time. Once the
tcpSerSock.listen(5)
                         # connections are full, others will be rejected.

video_dir.setup(busnum=busnum)
car_dir.setup(busnum=busnum)
# Initialize the Raspberry Pi GPIO connected to the DC motor.
motor.setup(busnum=busnum)
video_dir.home_x_y()
car_dir.home()




#camera
camera = cv2.VideoCapture(0)
camera.set(3, 320)
camera.set(4, 240)
return_value, image = camera.read()
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
close = 0




def sendImage():
    ret, frame = camera.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    #    data = zlib.compress(pickle.dumps(frame, 0))
    #data = "hola"
    data = pickle.dumps(frame, 0)
    size = len(data)

    #conn.sendall(data.encode())
    #sprint"{}: {}".format(img_counter, size))
    conn.sendall(struct.pack(">L", size) + data)


while close == 0:
	print ('Waiting for connection...')
	# Waiting for connection. Once receiving a connection, the function accept() returns a separate
	# client socket for the subsequent communication. By default, the function accept() is a blocking
	# one, which means it is suspended before the connection comes.
	tcpCliSock, addr = tcpSerSock.accept()
	ret, frame = cam.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
	data = pickle.dumps(frame, 0)
    size = len(data)
    #print("{}: {}".format(img_counter, size))
    client_socket.sendall(struct.pack(">L", size) + data)
	print ('...connected from :', addr)     # Print the IP address of the client connected with the server.
	while True:

		data = tcpCliSock.recv(BUFSIZ)    # Receive data sent from the client. 
		# Analyze the command received and control the car accordingly.
		if not data:
			break
		if data == ctrl_cmd[0]:
			print ('motor moving forward')
			motor.forward()
		elif data == ctrl_cmd[1]:
			print ('recv backward cmd')
			motor.backward()
		elif data == ctrl_cmd[2]:
			print ('recv left cmd')
			car_dir.turn_left()
		elif data == ctrl_cmd[3]:
			print ('recv right cmd')
			car_dir.turn_right()
		elif data == ctrl_cmd[6]:
			print ('recv home cmd')
			car_dir.home()
		elif data == ctrl_cmd[4]:
			print ('recv stop cmd')
			motor.ctrl(0)
		elif data == ctrl_cmd[5]:
			print ('read cpu temp...')
			temp = cpu_temp.read()
			tcpCliSock.send('[%s] %0.2f' % (ctime(), temp))
		elif data == ctrl_cmd[8]:
			print ('recv x+ cmd')
			video_dir.move_increase_x()
		elif data == ctrl_cmd[9]:
			print ('recv x- cmd')
			video_dir.move_decrease_x()
		elif data == ctrl_cmd[10]:
			print ('recv y+ cmd')
			video_dir.move_increase_y()
		elif data == ctrl_cmd[11]:
			print ('recv y- cmd')
			video_dir.move_decrease_y()
		elif data == ctrl_cmd[12]:
			print ('home_x_y')
			video_dir.home_x_y()
		elif data == ctrl_cmd[13]:
			print ('close')
			close=1
		elif data[0:5] == 'speed':     # Change the speed
			print (data)
			numLen = len(data) - len('speed')
			if numLen == 1 or numLen == 2 or numLen == 3:
				tmp = data[-numLen:]
				print ('tmp(str) = %s' % tmp)
				spd = int(tmp)
				print ('spd(int) = %d' % spd)
				if spd < 24:
					spd = 24
				motor.setSpeed(spd)

		elif data[0:5] == 'turn=':	#Turning Angle
			print ('data =', data)
			angle = data.split('=')[1]
			try:
				angle = int(angle)
				car_dir.turn(angle)
			except:
				print ('Error: angle =', angle
		elif data[0:8] == 'forward=':
			print ('data =', data)
			spd = data[8:]
			try:
				spd = int(spd)
				motor.forward(spd)
			except:
				print ('Error speed =', spd)
                elif data[0:9] == 'backward=':
                        print ('data =', data)
                        spd = data.split('=')[1]
			try:
				spd = int(spd)
	                        motor.backward(spd)
			except:
				print ('ERROR, speed =', spd)
		else:
			print ('Command Error! Cannot recognize command: ' + data)
        
        sendImage


camera.release()
writeFile.close()
tcpSerSock.close()
print ('save data')


