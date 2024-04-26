'''
db
database file, containing all the logic to interface with the sql database
'''

import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

#add friend
def save_friend(user1: str, user2: str):

    with Session(engine) as session:
        # Create two Friend objects to represent the bidirectional friendship
        friend1 = Friend(user_username1=user1, user_username2=user2)
        friend2 = Friend(user_username1=user2, user_username2=user1)

        session.add(friend1)
        session.add(friend2)
        session.commit()

#add_friend(username: str,friendname: str):
def get_friend(user: str, user2: str):

    with Session(engine) as session:
        # Try to find the friendship where user is user_username1 and user2 is user_username2
        friend = session.query(Friend).filter_by(user_username1=user, user_username2=user2).first()
        if friend:
            return friend

        # Try to find the friendship where user is user_username2 and user2 is user_username1
        friend = session.query(Friend).filter_by(user_username2=user, user_username1=user2).first()
        return friend


def get_friendlist(username: str):
    with Session(engine) as session:
        if username:
            user = session.query(User).filter_by(username=username).first()  # Get the User object by username
            friends = session.query(Friend).filter_by(user_username1=user.username).all()
            friend_usernames = [friend.user_username2 for friend in friends]
            return friend_usernames
        return []


#insert friend


#insert friend list:
def get_friendrequestlist(user: str):



    with Session(engine) as session:
        if user:
            requests = session.query(FriendRequest).filter_by(receiver_username=user).all()
            request_details = [f"{request.sender_username}, status: {request.status}" for request in requests]
            return request_details
        return []


def get_friendrequest(sender: str, receiver: str):
    with Session(engine) as session:
        if sender and receiver:
            friend_request = session.query(FriendRequest).filter_by(
                sender_username=sender,
                receiver_username=receiver
            ).first()
            return friend_request
    return None


def save_friendrequest(sender: str, receiver: str):

    if sender and receiver:
        with Session(engine) as session:
            friend_request = FriendRequest(sender_username=sender, receiver_username=receiver)
            session.add(friend_request)
            session.commit()
            return True
    return False
def update_friendrequest(sender: str, receiver: str,status: str):
    with Session(engine) as session:
        friend_request = session.query(FriendRequest).filter_by(
            sender_username=sender,
            receiver_username=receiver
        ).first()

        if friend_request:
            friend_request.status = status
            session.commit()
            return True
        return False

def save_message(roomid:int,sender: str, receiver: str, message: str):
    with Session(engine) as session:
        if sender and receiver:
            chat_msg = ChatRecord(chatroom_id=roomid,sender_username=sender,receiver_username=receiver,message=message)
            session.add(chat_msg)
            print(f'added {chat_msg}')
            session.commit()
            return True
        return False
def get_messagelist(sender:str, receiver: str):
    with Session(engine) as session:
        if sender and receiver:
            db_room_id = get_room(sender, receiver)
            if -1 == db_room_id:
                return []
            chat_records = session.query(ChatRecord).filter_by(chatroom_id=db_room_id).all()
            msg_content = [{"sender":msg.sender_username,"content":msg.message} for msg in chat_records]
            return msg_content
if __name__ == '__main__':



    # Assuming you have already configured your database URL
    engine = create_engine('sqlite:///database/main.db')  # Adjust for your actual database URL


    def check_friend_requests_for_kai():
        with Session(engine) as session:
            # Query FriendRequest for 'kai'
            requests = session.query(FriendRequest).filter_by(receiver_username='hank').all()
            if not requests:
                print("No friend requests found for hank.")
            else:
                for request in requests:
                    print(
                        f"Friend request from {request.sender_username} to {request.receiver_username} with status {request.status}")


    # Call the function
    check_friend_requests_for_kai()

