from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)

# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    admin = db.Column(db.Boolean)

    def __init__(self, username, password, admin):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")
        self.admin = admin

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title, description, done, user_id):
        self.title = title
        self.description = description
        self.done = done
        self.user_id = user_id

# Task Schema
class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "description", "done", "user_id")

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password", "admin")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Create a User
@app.route("/user/add", methods=["POST"])
def add_user():
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    admin = post_data.get("admin")
    user = db.session.query(User).filter_by(username=username).first()

    if user is not None:
        return jsonify({"message": "User already exists!"})                     

    encrypted_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username, encrypted_password, admin)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"})

# Get All Users
@app.route("/user", methods=["GET"])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

# Get Single User   
@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

# Update a User
@app.route("/user/<id>", methods=["PUT"])
def update_user(id):
    user = User.query.get(id)
    username = request.json["username"]
    password = request.json["password"]
    admin = request.json["admin"]

    user.username = username
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
    user.admin = admin

    db.session.commit()

    return user_schema.jsonify(user)

# Delete User
@app.route("/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

# Create a Task
@app.route("/task/add", methods=["POST"])
def add_task():
    post_data = request.get_json()
    title = post_data.get("title")
    description = post_data.get("description")
    done = post_data.get("done")
    user_id = post_data.get("user_id")
    new_task = Task(title, description, done, user_id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created successfully!"})

# Get All Tasks
@app.route("/task", methods=["GET"])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)

# Get Single Task
@app.route("/task/<id>", methods=["GET"])
def get_task(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)

# Update a Task
@app.route("/task/<id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get(id)
    title = request.json["title"]
    description = request.json["description"]
    done = request.json["done"]
    user_id = request.json["user_id"]

    task.title = title
    task.description = description
    task.done = done
    task.user_id = user_id

    db.session.commit()

    return task_schema.jsonify(task)

# Delete Task
@app.route("/task/<id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)



if __name__ == "__main__":
    app.run(debug=True)
