from base64 import encode
from numpy.lib.type_check import imag
import socketio
import cv2
import socketio
import base64
from io import BytesIO


sio = socketio.Client()
camera = cv2.VideoCapture(0)
camera.set(3, 320)
camera.set(4, 240)

img_counter = 0
ret, frame = camera.read()


def send():
    contador = 0
    while contador < 1:
        image = encodeImagecv2()
        sio.emit('telemetry',
                 data={
                     'steering_angle': "1",
                     'throttle': "1",
                     'image': image
                 })
        contador += 1
        print 'Se han mandado = ',contador,' mensajes'
        


@sio.on("connet")
def connect():
    print'connection established'


@sio.on("steer")
def my_message(data):
    print('message received with ', data)
    steering_angle = float(data["steering_angle"])
    throttle = float(data["throttle"])
    move_car(steering_angle,throttle)
    
#'forward', 'backward', 'left', 'right',
def move_car(steering_angle, throttle):
    direction = ""
    if steering_angle==-1:
        direction = "left"
    if steering_angle==0:
        direction = "forward"
    if steering_angle==1:
        direction = "right"
    
    print"direccion", direction


def encodeImagecv2():
    _, frame = camera.read()
    # im_arr: image in Numpy one-dim array format.
    _, im_arr = cv2.imencode('.jpg', frame)
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    #print im_b64
    return im_b64

@sio.on("disconnect")
def disconnect():
    print'disconnected from server'

sio.connect('http://localhost:4567')
#encodeImagecv2()
send()

sio.wait()
