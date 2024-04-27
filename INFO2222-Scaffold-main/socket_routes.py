from flask_socketio import join_room, emit, leave_room
from flask import request
try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room
import db

room = Room()

@socketio.on('connect')
def connect():
    username, room_id = request.cookies.get("username"), request.cookies.get("room_id")
    if room_id and username:
        join_room(room_id)
        emit("incoming", f"{username} has connected", to=room_id)

@socketio.on('disconnect')
def disconnect():
    username, room_id = request.cookies.get("username"), request.cookies.get("room_id")
    if room_id and username:
        emit("incoming", f"{username} has disconnected", to=room_id)

@socketio.on("send")
def send(username, message, receiver):
    if not db.get_user(username) or not db.get_user(receiver):
        emit("error", "User does not exist")
        return
    room_id = db.get_room(username, receiver) or db.save_room(username, receiver)
    if room_id and db.save_message(room_id, username, receiver, message):
        emit("incoming", f"{username}: {message}", to=room_id)
    else:
        emit("error", "Failed to save or retrieve room")

@socketio.on("join")
def join(sender_name, receiver_name):
    if not db.get_user(receiver_name) or not db.get_user(sender_name):
        emit("error", "Unknown user!")
        return
    room_id = room.get_room_id(receiver_name) or room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", f"{sender_name} has joined the room. Now talking to {receiver_name}.", to=room_id)

@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", f"{username} has left the room.", to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on('requestfriend')
def handle_friendrequest(username, receiver):
    if username == receiver:
        emit("error", "You cannot send a friend request to yourself.")
        return
    if db.get_friend(username, receiver):
        emit("error", "You are already friends.")
        return
    if not db.get_user(receiver):
        emit("error", "Target user does not exist.")
        return
    if db.get_friendrequest(username, receiver):
        emit("error", "Friend request already sent.")
        return
    if db.save_friendrequest(username, receiver):
        emit("success", "Friend request sent.")

@socketio.on('acceptfriend')
def handle_acceptfriend(username, receiver):
    if username == receiver:
        emit("error", "You cannot send a friend request to yourself.")
        return
    if db.get_friend(username, receiver):
        emit("error", "You are already friends.")
        return
    if not db.get_user(receiver):
        emit("error", "Target user does not exist.")
        return
    if not db.get_friendrequest(receiver, username):
        emit("error", "No friend request found.")
        return
    if db.update_friendrequest(receiver, username, "accepted"):
        emit("success", "Friend request accepted.")
