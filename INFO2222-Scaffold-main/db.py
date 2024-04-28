import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *
from pathlib import Path
import bcrypt
import os
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import urlsafe_b64encode

Path("database").mkdir(exist_ok=True)
engine = create_engine("sqlite:///database/main.db", echo=False)



# +++++++++++ user functions +++++++++++ #
def insert_user(username: str, password: str):
    hashed_password = hash_password(password)
    dkey = derive_key(password)
    with Session(engine) as session:
        user = User(username=username, password=hashed_password, key=dkey)
        session.add(user)
        session.commit()


def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)


# encryption for the user creat
def hash_password(password):
    """Hash a password for storing."""
    password = password.encode('utf-8')  # Ensure the password is in bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed


def check_password(stored_password, provided_password):
    provided_password = provided_password.encode('utf-8')

    return bcrypt.checkpw(provided_password, stored_password)


def derive_key(password: str, key_length=32):
    """Derive a cryptographic key from a password."""
    salt = bcrypt.gensalt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key


# +++++++++++ Friendship Functions +++++++++++ #
def save_friend(user1: str, user2: str):
    with Session(engine) as session:
        friend1 = Friend(user_username1=user1, user_username2=user2)
        friend2 = Friend(user_username1=user2, user_username2=user1)
        session.add_all([friend1, friend2])
        session.commit()


def get_friend(user: str, user2: str):
    with Session(engine) as session:
        friend = session.query(Friend).filter_by(user_username1=user, user_username2=user2).first()
        if not friend:
            friend = session.query(Friend).filter_by(user_username2=user, user_username1=user2).first()
        return friend


def get_friend_list(username: str):
    with Session(engine) as session:
        friends = session.query(Friend).filter_by(user_username1=username).all()
        return [friend.user_username2 for friend in friends]


# +++++++++++ Friend Request Functions +++++++++++ #
def save_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        friend_request = FriendRequest(sender_username=sender, receiver_username=receiver)
        session.add(friend_request)
        session.commit()
        return True


def get_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        return session.query(FriendRequest).filter_by(sender_username=sender, receiver_username=receiver).first()


def update_friend_request(sender: str, receiver: str, status: str):
    with Session(engine) as session:
        friend_request = session.query(FriendRequest).filter_by(sender_username=sender,
                                                                receiver_username=receiver).first()
        if friend_request:
            friend_request.status = status
            session.commit()
            return True
        return False


def get_friend_request_list(user: str):
    with Session(engine) as session:
        requests = session.query(FriendRequest).filter_by(receiver_username=user).all()
        return [f"{request.sender_username}, status: {request.status}" for request in requests]


# +++++++++++ Message Encryption +++++++++++ #
def encrypt_message(key, plaintext):
    """Encrypt a message using AES encryption."""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.urlsafe_b64encode(iv + ciphertext)

def decrypt_message(key, ciphertext):
    """Decrypt a message using AES decryption."""
    ciphertext = base64.urlsafe_b64decode(ciphertext)
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()


# +++++++++++ Message Functions +++++++++++ #
def save_message(roomid: int, sender: str, receiver: str, message: str):
    with Session(engine) as session:
        user = get_user(sender)
        key = user.key
        message = encrypt_message(key,message)
        chat_msg = ChatRecord(chatroom_id=roomid, sender_username=sender, receiver_username=receiver, message=message,
                              key=key)
        session.add(chat_msg)
        session.commit()
        return True


def get_message_list(sender: str, receiver: str):
    with Session(engine) as session:
        db_room_id = get_room(sender, receiver)
        chat_records = session.query(ChatRecord).filter_by(chatroom_id=db_room_id).all()
        return [{"sender": msg.sender_username, "content": msg.message, "key": msg.key} for msg in chat_records]


def delete_all_chat_data():
    """Delete all data from ChatRoom and ChatRecords tables."""
    with Session(engine) as session:
        try:
            # Delete all records in ChatRecords first due to foreign key constraints
            session.query(ChatRecord).delete()
            # Then delete all records in ChatRoom
            session.query(RoomDB).delete()
            session.commit()
            print("All data in ChatRoom and ChatRecords have been deleted.")
        except Exception as e:
            session.rollback()
            print(f"Failed to delete data: {e}")




if __name__ == '__main__':

    with Session(engine) as session:
        user = get_user("kai")
        print(user.password)

        msglist = get_messagelist("alice","bob")

        if len(msglist) > 0:
            for msg in msglist:
                sender = msg['sender']
                content = msg['content']
                key = msg['key']
                decrypt = decrypt_message(key, content)
                print(content,decrypt)





