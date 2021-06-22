import eventlet
import base64
import socketio
from flask import Flask
from PIL import Image
from io import BytesIO

#initialize our server
sio = socketio.Server()
#our flask (web) app
app = Flask(__name__)
#init our model and image array as empty
@sio.on('connet')
def connect(sid, environ):
    print('connect ', sid)
    send_control(0,0)

@sio.on('telemetry')
def telemetry(sid, data):
    steering_angle = float(data["steering_angle"])
    # The current throttle of the car, how hard to push peddle
    throttle = float(data["throttle"])
    # The current speed of the car

    image = Image.open(BytesIO(base64.b64decode(data["image"])))

    print('message completo ', data)
    


def send_control(steering_angle, throttle):
    sio.emit(
        "steer",
        data={
            'steering_angle': steering_angle.__str__(),
            'throttle': throttle.__str__()
        },
        skip_sid=True)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('localhost', 4567)), app)
