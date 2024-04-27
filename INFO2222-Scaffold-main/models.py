'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, Column, Integer, TIMESTAMP, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from typing import Dict


engine = create_engine("sqlite:///database/main.db", echo=False)

# data models
class Base(DeclarativeBase):
    pass

# model to store user information

class User(Base):
    __tablename__ = 'tUsers'
    username = Column(String(50), primary_key=True)
    password = Column(String(255), nullable=False)
    # Relationships can be added here if necessary

class Friend(Base):
    __tablename__ = 'Friends'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_username1 = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    user_username2 = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    __table_args__ = (UniqueConstraint('user_username1', 'user_username2', name='_user_pair_uc'),)

class FriendRequest(Base):
    __tablename__ = 'FriendRequests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    receiver_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    status = Column(String, nullable=False, default='pending')

class ChatRecord(Base):
    __tablename__ = 'ChatRecords'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatroom_id = Column(Integer, nullable=False)
    sender_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    receiver_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    message = Column(String, nullable=False)

class ChatRoom(Base):
    __tablename__ = 'ChatRoom'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    creator_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    participant_username = Column(String(50), nullable=False)  # This might need adjustments based on your design


def get_room(creator: str, receiver: str):
    """Retrieve a room ID based on the creator and receiver."""
    with Session(engine) as session:
        room = session.query(ChatRoom).filter(
            ((ChatRoom.creator_username == creator) & (ChatRoom.participant_username == receiver)) |
            ((ChatRoom.creator_username == receiver) & (ChatRoom.participant_username == creator))
        ).first()

        if room:
            return room.id
        return None  # Return None if no room found



def get_room_by_id(room_id: int):
    """Retrieve a room by its ID."""
    with Session(engine) as session:
        room = session.query(RoomDB).filter_by(id=room_id).first()
        return room
def save_room(creator: str, receiver: str):
    """Save a room to the database, ensuring no duplicates exist."""
    with Session(engine) as session:
        # Check if room already exists to avoid duplicates
        existing_room = session.query(ChatRoom).filter(
            ((ChatRoom.creator_username == creator) & (ChatRoom.participant_username == receiver)) |
            ((ChatRoom.creator_username == receiver) & (ChatRoom.participant_username == creator))
        ).first()

        if existing_room:
            print("Room already exists.")
            return existing_room.id  # Return existing room ID if found

        # If no room exists, create a new one
        new_room = ChatRoom(creator_username=creator, participant_username=receiver, name=f"{creator}_{receiver}")
        session.add(new_room)
        session.commit()
        print(f"New room created with ID: {new_room.id}")
        return new_room.id



class RoomDB(Base):
    __tablename__ = 'tChatRoom'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    creator_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)
    participant_username = Column(String(50), ForeignKey('tUsers.username'), nullable=False)


def save_message(roomid: int, sender: str, receiver: str, message: str):
    with Session(engine) as session:
        if sender and receiver:
            chat_message = ChatRecord(chatroom_id=roomid,sender_username=sender,receiver_username=receiver,message=message)
            session.add(chat_message)
            session.commit()
            return True
        return False
def get_messagelist(sender: str ,receiver: str):
    with Session(engine) as session:
        if sender and receiver:
            room_id = get_room(sender, receiver)
            if room_id == -1:
                return []
            chat_records = session.query(ChatRecord).filter_by(chatroom_id=room_id).al1()
            messages_content = [{"sender":msg.sender_username,"content":msg.message} for msg in chat_records]
            return messages_content
        return []

                








# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    def get_room_receiver(self,room_id: int,exclusion:str ):
        print(self.dict)
        for key,value in self.dict.items():
            if value == room_id and value != exclusion:
                return key
        return None

    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
