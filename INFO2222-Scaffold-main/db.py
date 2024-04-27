import sqlalchemy as db
from sqlalchemy.orm import Session
from models import User, Friend, FriendRequest, ChatRecord, ChatRoom, Base
from sqlalchemy import create_engine
from pathlib import Path

# Establish the database connection
engine = create_engine('sqlite:///database/main.db', echo=True)
Base.metadata.create_all(engine)  # Ensure all tables are created based on models

def get_user(username):
    """Retrieve a user from the database by username."""
    with Session(engine) as session:
        return session.query(User).filter_by(username=username).first()

def insert_user(username, password):
    """Insert a new user into the database."""
    with Session(engine) as session:
        if not get_user(username):
            user = User(username=username, password=password)
            session.add(user)
            session.commit()
            return True
        return False

def save_friend(user1, user2):
    """Create a friend connection between two users."""
    with Session(engine) as session:
        if not session.query(Friend).filter_by(user_username1=user1, user_username2=user2).first():
            friend1 = Friend(user_username1=user1, user_username2=user2)
            friend2 = Friend(user_username1=user2, user_username2=user1)
            session.add_all([friend1, friend2])
            session.commit()
            return True
        return False

def get_friend(user1, user2):
    """Check if two users are friends."""
    with Session(engine) as session:
        return session.query(Friend).filter_by(user_username1=user1, user_username2=user2).first()

def save_friendrequest(sender, receiver):
    """Save a new friend request."""
    with Session(engine) as session:
        if not session.query(FriendRequest).filter_by(sender_username=sender, receiver_username=receiver).first():
            friend_request = FriendRequest(sender_username=sender, receiver_username=receiver)
            session.add(friend_request)
            session.commit()
            return True
        return False

def get_friendrequest(sender, receiver):
    """Retrieve a friend request from one user to another."""
    with Session(engine) as session:
        return session.query(FriendRequest).filter_by(sender_username=sender, receiver_username=receiver).first()

def update_friendrequest(sender, receiver, status):
    """Update the status of a friend request."""
    with Session(engine) as session:
        friend_request = get_friendrequest(sender, receiver)
        if friend_request:
            friend_request.status = status
            session.commit()
            return True
        return False


def get_friendrequestlist(user: str):
    """
    Retrieves a list of friend requests where the given user is the receiver.

    Parameters:
        user (User): The user who has received the friend requests.

    Returns:
        list[str]: A list of strings with sender username and request status, or an empty list if no user.
    """
    if not user:
        return []

    with Session(engine) as session:
        requests = session.query(FriendRequest).filter_by(receiver_username=user).all()
        request_details = [f"{request.sender_username}, status: {request.status}" for request in requests]
        return request_details
def get_friendlist(username):
    """ Retrieve the friend list for a user """
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            friends = session.query(Friend).filter((Friend.user_username1 == username) | (Friend.user_username2 == username)).all()
            friend_usernames = []
            for friend in friends:
                if friend.user_username1 == username:
                    friend_usernames.append(friend.user_username2)
                else:
                    friend_usernames.append(friend.user_username1)
            return friend_usernames
        return []


def get_room(sender, receiver):
    """Retrieve or create a room for communication between two users."""
    with Session(engine) as session:
        room = session.query(ChatRoom).filter(
            ((ChatRoom.creator_username == sender) & (ChatRoom.participant_username == receiver)) |
            ((ChatRoom.creator_username == receiver) & (ChatRoom.participant_username == sender))
        ).first()
        return room.id if room else None

def save_room(sender, receiver):
    """Save a new chat room if it does not exist."""
    with Session(engine) as session:
        room_id = get_room(sender, receiver)
        if not room_id:
            new_room = ChatRoom(creator_username=sender, participant_username=receiver)
            session.add(new_room)
            session.commit()
            return new_room.id
        return room_id

def save_message(room_id, sender, receiver, message):
    """Save a message sent from one user to another in a chat room."""
    with Session(engine) as session:
        new_message = ChatRecord(chatroom_id=room_id, sender_username=sender, receiver_username=receiver, message=message)
        session.add(new_message)
        session.commit()

def get_messagelist(room_id):
    """Retrieve all messages from a chat room."""
    with Session(engine) as session:
        messages = session.query(ChatRecord).filter_by(chatroom_id=room_id).all()
        return [{"sender": m.sender_username, "message": m.message} for m in messages]

# Create the database directory if it doesn't exist
Path("database").mkdir(exist_ok=True)
