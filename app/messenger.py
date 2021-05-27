from app import socketio, db
from flask import session, request
from flask_login import current_user
from flask_socketio import send, emit, join_room, leave_room
from time import sleep
from app.models import Message


clients = {'user.id': 'session.id'}


@socketio.event
def send_to(from_id, data):
    print('message sended form event')


@socketio.on('send_from')
def send_message(data, target_id):
    print(data)
    print(target_id)
    print(clients[target_id])

    message = Message(sender_id=current_user.id,
                      receiver_id=target_id,
                      body=data)
    db.session.add(message)
    db.session.commit()

    emit('send_to', {'data': data, 'from_id': request.sid}, to=clients[target_id])
    print('message sended')


@socketio.on('user_connect')
def connect(user_id):
    print(f'hello {user_id}')
    clients[user_id] = request.sid
    join_room(request.sid)

    print(clients)


@socketio.on('message')
def handle_message(data):
    print(f'{request.sid}')
    print(f'received message: {data}')
    while True:
        send('hello')
        sleep(5)

