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
    print("send enter")
    emit("incoming", (f"{username}: {message}"), to=room_id)
    receiver = room.get_room_receiver(int(room_id), username)
    if receiver is None:
        print("receiver does not exist")
        return
    print(f'receiver : {receiver}')

    db_room_id = db.get_room(username,receiver)
    if db_room_id is None:
        print("room does not exist")
        db.save_room(username,receiver)
    print(f"db_room_id1:{db_room_id}, username:{username},receiver:{receiver},message:{message}")
    db_room_id = db.get_room(username,receiver)
    if db_room_id is None:

        print("room does not exist again")
        return
    print(f"db_room_id2:{db_room_id}, username:{username},receiver:{receiver}")
    print(f"send result = {db.save_message(db_room_id,username,receiver,message)},message:{message}")

# @socketio.on("send")
# def send(username, message, receiver):
#     print("Attempting to send message...")
#     room_id = db.get_room(username, receiver)  # Get the existing room ID or create a new one
#
#     if room_id is None:
#         room_id = db.save_room(username, receiver)  # Create room if it doesn't exist
#
#     if room_id is not None:
#         if db.save_message(room_id, username, message):
#             print("Message saved successfully.")
#             emit("incoming", {"sender": username, "message": message}, to=room_id)
#         else:
#             print("Failed to save message.")
#     else:
#         print("Failed to retrieve or create room.")



# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

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
                emit("incoming", (f"{sender}: {content}","green"), to=room_id)

        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


@socketio.on('requestfriend')
def handle_friendrequest(username, receiver):
    """
    Handles a friend request event from one user to another.

    Parameters:
        username (str): The username of the user sending the friend request.
        receiver (str): The username of the user receiving the friend request.

    Returns:
        str: A message indicating the result of the friend request operation.
    """
    # 1. Check if they are already friends
    friend = db.get_friend(username, receiver)
    if friend is not None:
        return "You are already friends."

    # 2. Check if the target user exists
    target = db.get_user(receiver)
    if target is None:
        return "Target user does not exist."

    # 3. Check if there is already a friend request pending
    friend_request = db.get_friendrequest(username, receiver)
    if friend_request is not None:
        return "Friend request already sent."
    # 4. can not send to yourself
    if username == receiver:
        return "you can not send friend request to yourself."


    # 5. Save the friend request
    db.save_friendrequest(username,receiver)
    return "Friend request sent."

@socketio.on('acceptfriend')
def handle_acceptfriend(username, receiver):
    # 0. Check you can't send a friend request to yourself
    if username == receiver:
        return "You can't send a friend request to yourself."

    # 1. Check if they are already friends
    friend = db.get_friend(receiver,username)
    if friend is not None:
        return "You are already friends."

    # 2. Check if the target user exists
    target = db.get_user(receiver)
    if target is None:
        return "Target user does not exist."

    # 3. Check if there is a pending friend request
    friend_request = db.get_friendrequest( receiver,username)
    if friend_request is None:
        return "No friend request found."

    # If there is a friend request, accept it here (you may need to add logic for this)
    # For now, we assume accepting the friend request means adding them as friends
    db.save_friend(receiver,username)
    db.update_friendrequest(receiver,username,"accepted")
    return "Friend request accepted."




