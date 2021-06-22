import cv2
import io
import struct
import time
import pickle
import zlib
import csv
from Tkinter import *
from socket import *
from threading import Thread

window=Tk()
#cv2.imwrite(imagePath,image)
BUFSIZ = 1024
flagThread=True
imagePath = "/Users/jorgearmenta/Desktop/tesis/data/IMG/img"
#csv_path_file = "/home/pi/data/data.csv"
csvPathFile = "/Users/jorgearmenta/Desktop/tesis/data/driving_log.csv"
#clientSocket = socket.socket(AF_INET, socket.SOCK_STREAM)
#clientSocket.connect(('192.168.1.76', 8485))
#clientSocket.connect(('192.168.1.104', 8485))
#connection = clientSocket.makefile('wb')
HOST = '192.168.1.74'    # Server(Raspberry Pi) IP address oficina
PORT = 21567
BUFSIZ = 1024             # buffer size
ADDR = (HOST, PORT)

clientSocket = socket(AF_INET, SOCK_STREAM)   # Create a socket
clientSocket.connect(ADDR)
countImg = -1
matrix = []
#imagen, angulo (izquierda -1, derecha 1),aceleracion adelante, aceleracion atras, rapidez
array = ["", 0, 0, 0, 0]


#print"payload_size: {}".format(payload_size))


def forward_fun(event):
    print'forward'
    array[2] = 1
    array[3] = 0
    array[1] = 0
    clientSocket.send(b'backward')


def backward_fun(event):
    print'backward'
    array[3] = 1
    clientSocket.send(b'forward')


def left_fun(event):
    print'left'
    array[1]=-1
    array[2]=1
    clientSocket.send(b'left')


def right_fun(event):
    print'right'
    array[1]=1
    array[2]=1
    clientSocket.send(b'right')


def stop_fun(event):
    print'stop'
    clientSocket.send(b'stop')


def home_fun(event):
    print'home'
    clientSocket.send(b'home')


def quit_fun(event):
    flagThread = False
    saveArray()
    window.quit()
    clientSocket.send(b'stop')
    clientSocket.close()
    
    

# =============================================================================
# Create buttons
# =============================================================================
Btn0 = Button(window, width=5, text='Forward')
Btn1 = Button(window, width=5, text='Backward')
Btn2 = Button(window, width=5, text='Left')
Btn3 = Button(window, width=5, text='Right')
Btn4 = Button(window, width=5, text='Quit')
Btn5 = Button(window, width=5, height=2, text='Home')

# =============================================================================
# Buttons layout
# =============================================================================
Btn0.grid(row=0, column=1)
Btn1.grid(row=2, column=1)
Btn2.grid(row=1, column=0)
Btn3.grid(row=1, column=2)
Btn4.grid(row=3, column=2)
Btn5.grid(row=1, column=1)

# =============================================================================
# Bind the buttons with the corresponding callback function.
# =============================================================================
# When button0 is pressed down, call the function forward_fun().
Btn0.bind('<ButtonPress-1>', forward_fun)
Btn1.bind('<ButtonPress-1>', backward_fun)
Btn2.bind('<ButtonPress-1>', left_fun)
Btn3.bind('<ButtonPress-1>', right_fun)
# When button0 is released, call the function stop_fun().
Btn0.bind('<ButtonRelease-1>', stop_fun)
Btn1.bind('<ButtonRelease-1>', stop_fun)
Btn2.bind('<ButtonRelease-1>', stop_fun)
Btn3.bind('<ButtonRelease-1>', stop_fun)
Btn4.bind('<ButtonRelease-1>', quit_fun)
Btn5.bind('<ButtonRelease-1>', home_fun)


# =============================================================================
# Bind buttons on the keyboard with the corresponding callback function to
# control the car remotely with the keyboard.
# =============================================================================
# Press down key 'A' on the keyboard and the car will turn left.
window.bind('<KeyPress-a>', left_fun)
window.bind('<KeyPress-d>', right_fun)
window.bind('<KeyPress-s>', backward_fun)
window.bind('<KeyPress-w>', forward_fun)
window.bind('<KeyPress-h>', home_fun)
# Release key 'A' and the car will turn back.
window.bind('<KeyRelease-a>', stop_fun)
window.bind('<KeyRelease-d>', stop_fun)
window.bind('<KeyRelease-s>', stop_fun)
window.bind('<KeyRelease-w>', stop_fun)

spd = 60


def changeSpeed(ev=None):
	tmp = 'speed'
	global spd
	spd = speed.get()
	# Change the integers into strings and combine them with the string 'speed'.
	data = tmp + str(spd)
	print ('sendData = '+str(data))
	clientSocket.send(data)  # Send the speed data to the server(Raspberry Pi)


label = Label(window, text='Speed:', fg='red')  # Create a label
label.grid(row=6, column=0)                  # Label layout

speed = Scale(window, from_=0, to=100, orient=HORIZONTAL,
              command=changeSpeed)  # Create a scale
speed.set(50)
speed.grid(row=6, column=1)


def saveImage():
    data = b""
    payload_size = struct.calcsize(">L")
    
    while len(data) < payload_size:
        #print"Recv: {}".format(len(data)))
        data += clientSocket.recv(4096)
    #print"Done Recv: {}".format(len(data)))

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    #print"msg_size: {}".format(msg_size))

    while len(data) < msg_size:
        data += clientSocket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    global countImg
    countImg = countImg + 1
    
    array[0] = imagePath+str(countImg)+".jpg"
    newList = array[:]
    matrix.append(newList)
    #print (matrix)
    clientSocket.send(b'stop')
    clientSocket.send(b'home')
    cv2.imwrite(imagePath+str(countImg)+".jpg", frame)
    print 'Imagen Guardada N.', str(countImg), array[1],array[2]
    clientSocket.send(b'stop')
    clientSocket.send(b'home')


def saveArray():
    with open(csvPathFile, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(matrix)
    
def receive():  # Recibe Mensaje del Broadcast
    while flagThread:
        try:
             #mensaje = clientSocket.recv(BUFSIZ).decode("utf8")
            saveImage()
            #printmensaje)
        except OSError as error:
            print"error",error
            break


def main():
    receive_thread = Thread(target=receive)
    receive_thread.start()
    window.mainloop()


if __name__ == '__main__':
	main()
