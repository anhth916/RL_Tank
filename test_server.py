import argparse
import base64
from datetime import datetime
import os
import shutil
import numpy as np
import socketio
import eventlet
import eventlet.wsgi
from PIL import Image
from flask import Flask
from io import BytesIO


#initialize our server
sio = socketio.Server()
#our flask (web) app
app = Flask(__name__)
#init our model and image array as empty

#registering event handler for the server



@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)

# called every frame and transfer data from game
@sio.on('telemetry_0')
def telemetry(sid, data):
    enemy_pos = data["enemy_pos"]
    x = enemy_pos["x"]
    y = enemy_pos["y"]
    send_control(1,[x,y])

#send control to game(action:  1 is fire, 0 is move to)
def send_control(action, pos):
    sio.emit(
        "control",
        data={
            'action': action.__str__(),
            'pos_x': pos[0].__str__(),
            'pos_y': pos[1].__str__(),
        })


if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)