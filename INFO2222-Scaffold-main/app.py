from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
import db
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

import socket_routes  # Import the socket routes

@app.route("/")
def index():
    return render_template("index.jinja")

@app.route("/login")
def login():
    return render_template("login.jinja")

@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")
    user = db.get_user(username)
    if not user or user.password != password:
        return "Error: User or Password does not exist!"

    return url_for('home', username=username)

@app.route("/signup")
def signup():
    return render_template("signup.jinja")

@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")
    if db.insert_user(username, password):
        return url_for('home', username=username)
    return "Error: User already exists!"

@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

@app.route("/home")
def home():
    username = request.args.get("username")
    if not username or not db.get_user(username):
        abort(404)
    friendlist = db.get_friendlist(username)
    friendreqlist = db.get_friendrequestlist(username)  # Fetch friend requests
    return render_template("home.jinja", username=username, friend_list=friendlist, friend_req_list=friendreqlist)

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
