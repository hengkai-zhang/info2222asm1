drop table tUsers;
drop table tFriends;
drop table tChatRecords;
drop table tChatRoom;
drop table tFriendRequests;

-- Table for Users
CREATE TABLE tUsers (
    username VARCHAR(50) NOT NULL PRIMARY KEY,
    password VARCHAR(255) NOT NULL ,-- hash
    key VARCHAR(255) NOT NULL
);

-- Table for Friendship relationships
CREATE TABLE tFriends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_username1 VARCHAR(50) NOT NULL,
    user_username2 VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_username1) REFERENCES tUsers(username),
    FOREIGN KEY (user_username2) REFERENCES tUsers(username),
    UNIQUE (user_username1, user_username2)
);

-- Table for Friend Requests
CREATE TABLE tFriendRequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_username VARCHAR(50) NOT NULL,
    receiver_username VARCHAR(50) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (sender_username) REFERENCES tUsers(username),
    FOREIGN KEY (receiver_username) REFERENCES tUsers(username),
    UNIQUE (sender_username, receiver_username),
    CHECK (status IN ('pending', 'accepted', 'rejected'))
);


-- Table for Chat Records
CREATE TABLE tChatRecords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chatroom_id INT NOT NULL,
    sender_username VARCHAR(50) NOT NULL,
    receiver_username VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (sender_username) REFERENCES tUsers(username),
    FOREIGN KEY (receiver_username) REFERENCES tUsers(username),
    key VARCHAR(255) NOT NULL
);

-- Table for Chat Rooms -- speed check records
CREATE TABLE tChatRoom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    creator_username VARCHAR(50) NOT NULL,
    participant_username VARCHAR(50) NOT NULL
);

-- Table for the

select * from tChatRoom



