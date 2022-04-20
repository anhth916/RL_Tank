import socketio
import eventlet
import configparser
import eventlet.wsgi

from flask import Flask



#initialize our server
sio = socketio.Server()
#our flask (web) app
app = Flask(__name__)
#init our model and image array as empty

#registering event handler for the server
@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    
@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

# called every frame and transfer data from game
@sio.on('telemetry_1')
def telemetry(sid, data):
    sio.emit("radio_tank_1", data=data)
    
@sio.on('telemetry_2')
def telemetry(sid, data):
    sio.emit("radio_tank_2", data=data)
    
@sio.on('radio_tank_1_reply')
def radio_tank_1_reply(sid, data):
    sio.emit("tank_control_1", data=data)
    
@sio.on('radio_tank_2_reply')
def radio_tank_1_reply(sid, data):
    sio.emit("tank_control_2", data=data)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(r'C:\Users\Msi\Documents\FSoft_QAI\RL_Tank\game_server.cfg')
    
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)
    address = config.get('SOCKET', 'SOCKET_SERVER_ANDDRESS')  
    port = int(config.get('SOCKET', 'SOCKET_PORT'))
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen((address, port)), app)