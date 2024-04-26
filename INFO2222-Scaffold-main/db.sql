drop table tUsers;
drop table tFriends;
drop table tChatRecords;
drop table tChatRoom;
drop table tFriendRequests;

-- Table for Users
CREATE TABLE tUsers (
    username VARCHAR(50) NOT NULL PRIMARY KEY,
    password VARCHAR(255) NOT NULL -- hash
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
    CREATE TABLE tFriendRequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_username VARCHAR(50) NOT NULL,
    receiver_username VARCHAR(50) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_username) REFERENCES tUsers(username),
    FOREIGN KEY (receiver_username) REFERENCES tUsers(username)
);

-- Table for Chat Rooms -- speed check records
CREATE TABLE tChatRoom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creator_username VARCHAR(50) NOT NULL,
    participant_username VARCHAR(50) NOT NULL
);

-- Inserting into tUsers table
INSERT INTO tUsers (username, password) VALUES
  ('walter', '4567'),
  ('jdavis', '0123');

-- Inserting into Friends table
INSERT INTO tFriends (user_username1, user_username2) VALUES
  ('jdavis', 'walter'),
  ('walter', 'jdavis'),
  ('jdavis', 'jessica'),
  ('jessica', 'jdavis'),
  ('walter', 'bob'),
  ('bob', 'walter');

-- Inserting into tFriendRequests table
INSERT INTO tFriendRequests (sender_username, receiver_username) VALUES
  ('jdavis', 'walter'),
  ('jdavis', 'jessica'),
  ('jessica', 'jdavis'),
  ('jessica', 'bob'),
  ('bob', 'jessica');

-- Inserting into tChatRoom table
INSERT INTO tChatRoom (name, creator_username, participant_username) VALUES
  ('jdavis_and_walter', 'jdavis', 'walter'),
  ('jessica_and_bob', 'jessica', 'bob');

-- Inserting into ChatRecords table
INSERT INTO tChatRecords (chatroom_id, sender_username, receiver_username, message) VALUES
  (2, 'jdavis', 'walter', 'Hi Walter!'),
  (1, 'walter', 'jdavis', 'Hi JD!'),
  (1, 'jdavis', 'walter', 'How are you doing?'),
  (1, 'walter', 'jdavis', 'I am fine.'),
  (1, 'jdavis', 'walter', 'I am fine too.'),
  (2, 'jessica', 'bob', 'Hi Bob!'),
  (2, 'bob', 'jessica', 'Hi Jessica!'),
  (2, 'jessica', 'bob', 'How are you doing?');



