from sqlalchemy import String, Column, Integer, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from typing import Dict
from pathlib import Path
import os

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode

import db

engine = create_engine("sqlite:///database/main.db", echo=False)
Path("database").mkdir(exist_ok=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'tUsers'
    username = Column(String(50), primary_key=True)
    password = Column(String(255), nullable=False)
    key = Column(String, nullable=False)



class Friend(Base):
    __tablename__ = 'tFriends'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_username1 = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    user_username2 = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    __table_args__ = (UniqueConstraint('user_username1', 'user_username2', name='_user_pair_uc'),)


class FriendRequest(Base):
    __tablename__ = 'tFriendRequests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    receiver_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    status = Column(String, nullable=False, default='pending')


class ChatRecord(Base):
    __tablename__ = 'tChatRecords'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatroom_id = Column(Integer, nullable=False)
    sender_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    receiver_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    message = Column(String, nullable=False)
    key = Column(String, nullable=False)


class RoomDB(Base):
    __tablename__ = 'tChatRoom'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    creator_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    participant_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)


def get_room(creator: str, receiver: str):
    with Session(engine) as session:
        print(f"strat matching :creator :{creator} and receiver :{receiver}")
        room = session.query(RoomDB).filter_by(creator_username=creator, participant_username=receiver).first()
        rooms = session.query(RoomDB).all()
        print("all the rooms are shown")
        for r in rooms:
            print(f"room_id:{r.id},participant_username:{r.participant_username},creator_username:{r.creator_username}")

        if room is not None:
            print(f"the first check with id {room.id}")
            return room.id
        room = session.query(RoomDB).filter_by(creator_username=receiver, participant_username=creator).first()
        if room is not None:
            print(f"the second check with id {room.id}")
            return room.id
        return None


def get_room_receiver(room_id: int, username: str):
    with Session(engine) as session:
        room = session.query(RoomDB).filter_by(id=room_id).first()
        print(f"in this room creator is {room.creator_username},{room.participant_username}")
        if room.participant_username == username:
            return rooqm.creator_username
        if room.creator_username == username:
            return room.participant_username
        return None


def save_room(creator: str, receiver: str):
    with Session(engine) as session:
        existing_room = get_room(creator, receiver)
        if existing_room is not None:
            print(f"return exsisting room for {creator} and {receiver}")
            return existing_room
        if creator == receiver:
            print(f"creator == receiver")
            return None
        new_room = RoomDB(creator_username=creator, participant_username=receiver, name="room")
        session.add(new_room)
        session.commit()
        print(f"return new room for {creator} and {receiver}")
        return new_room.id


def save_message(roomid: int, sender: str, receiver: str, message: str):
    with Session(engine) as session:
        chat_message = ChatRecord(id=roomid, sender_username=sender, receiver_username=receiver,
                                  message=message)
        session.add(chat_message)
        session.commit()
        return True


def get_messagelist(sender: str, receiver: str):
    with Session(engine) as session:
        room_id = get_room(sender, receiver)
        if room_id is None:
            return []
        chat_records = session.query(ChatRecord).filter_by(chatroom_id=room_id).all()
        return [{"sender": msg.sender_username, "content": msg.message,"key": msg.key} for msg in chat_records]


class Counter():
    def __init__(self):
        self.counter = 0

    def get(self):
        self.counter += 1
        return self.counter


class Room():
    def __init__(self):
        self.counter = Counter()
        self.dict: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str):
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id


    def join_room(self, sender: str, room_id: int):
        self.dict[sender] = room_id

    def leave_room(self, user: str):
        self.dict.pop(user, None)

    def get_room_id(self, user: str):
        return self.dict.get(user)


if __name__ == "__main__":
    with Session(engine) as session:
        room = session.query(RoomDB).filter_by(creator_username="kai", participant_username="bob").first()
        print(room.id)
