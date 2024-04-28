'''
socket_routes
file containing all the routes related to socket.io
'''

from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()


# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))


# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    emit("incoming", (f"{username}: {message}"), to=room_id)
    receiver = db.get_room_receiver(int(room_id), username)

    if receiver is None:
        print("receiver does not exist")
        return
    print(f'receiver : {receiver}')
    db_room_id = db.get_room(username, receiver)
    if db_room_id is None:
        print("room does not exist")
        db.save_room(username, receiver)
    print(f"db_room_id1:{db_room_id}, username:{username},receiver:{receiver},message:{message}")
    db_room_id = db.get_room(username, receiver)
    if db_room_id is None:
        print("room does not exist again")
        return
    print(f"db_room_id2:{db_room_id}, username:{username},receiver:{receiver}")
    print(f"send result = {db.save_message(db_room_id, username, receiver, message)},message:{message}")





# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    print(f"is there a join question? {sender_name}{receiver_name}")
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    if receiver_name == sender_name:
        return "don't chat with yourself"

    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"


    room_id = db.save_room(sender_name,receiver_name)
    print(f"is there a get room question? ")
    db.get_room_receiver(room_id,sender_name)

    if room_id is not None:

        room.join_room(sender_name, room_id)
        join_room(room_id)
        db.save_room(sender_name, receiver_name)
        msglist = db.get_messagelist(sender_name, receiver_name)
        print(f"msglist: {msglist}")
        if len(msglist) > 0:
            for msg in msglist:
                sender = msg['sender']
                content = msg['content']
                key = msg['key']
                content = db.decrypt_message(key,content)
                emit("incoming", (f"{sender}: {content}", "green"), to=room_id)

        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)

        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        room_id = db.get_room(sender_name, receiver_name)
        print("in the  join, before sending ")
        db.get_room_receiver(room_id,sender_name)
        return room_id

    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    print("in the  join, before sending ")
    db.get_room_receiver(room_id, sender_name)
    return room_id


# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


@socketio.on('requestfriend')
def handle_friendrequest(username, receiver):

    friend = db.get_friend(username, receiver)
    if friend is not None:
        return "You are already friends."

    target = db.get_user(receiver)
    if target is None:
        return "Target user does not exist."

    friend_request = db.get_friend_request(username, receiver)
    if friend_request is not None:
        return "Friend request already sent."

    if username == receiver:
        return "you can not send friend request to yourself."

    # 5. Save the friend request
    db.save_friend_request(username, receiver)
    return "Friend request sent."


@socketio.on('acceptfriend')
def handle_acceptfriend(username, receiver):

    if username == receiver:
        return "You can't send a friend request to yourself."


    friend = db.get_friend(receiver, username)
    if friend is not None:
        return "You are already friends."


    target = db.get_user(receiver)
    if target is None:
        return "Target user does not exist."


    friend_request = db.get_friend_request(receiver, username)
    if friend_request is None:
        return "No friend request found."

    db.save_friend(receiver, username)
    db.update_friend_request(receiver, username, "accepted")
    return "Friend request accepted."




