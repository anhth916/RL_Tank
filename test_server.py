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
    config = configparser.ConfigParser()
    config.read('./game_server.cfg')
    
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)
    address = config.get('SOCKET', 'SOCKET_ANDDRESS')  
    port = int(config.get('SOCKET', 'SOCKET_PORT'))
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen((address, port)), app)