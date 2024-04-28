'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO

import db
import secrets


app = Flask(__name__)


# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    input_password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User or Password does not exist!"

    if not db.check_password(user.password,input_password):
        return "Error: User or Password does not exist!"

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    if db.get_user(request.args.get("username")) is None:
        abort(404)
    friend_list = db.get_friend_list(request.args.get("username"))
    friend_request_list = db.get_friend_request_list(request.args.get("username"))
    return render_template("home.jinja", username=request.args.get("username"), friend_list=friend_list, friend_req_list=friend_request_list)



if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
