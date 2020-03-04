from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data import teachers
import json
import random

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    about = db.Column(db.String(2048), nullable=False)
    picture = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Float)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String(255), nullable=False)
    free = db.Column(db.String(1024), nullable=False)
    booking = db.relationship('Booking', back_populates='teacher')


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    clientWeekday = db.Column(db.String(64), nullable=False)
    clientTime = db.Column(db.String(8), nullable=False)
    clientTeacher = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    clientName = db.Column(db.String(255), nullable=False)
    clientPhone = db.Column(db.String(255), nullable=False)
    teacher = db.relationship('Teacher', back_populates='booking')


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)


db.create_all()

# sampling free-time
for teacher in teachers:
    for day, value in teacher['free'].items():
        for time in value:
            value[time] = bool(random.choices([0, 1], weights=[4, 1])[0])

# Loading MOSK data to SQlite DB
tmp_lst = []
for one in teachers:
    teacher = Teacher(
        name=one['name'],
        about=one['about'],
        picture=one['picture'],
        rating=one['rating'],
        price=one['price'],
        goals=json.dumps(one['goals']),
        free=json.dumps(one['free']))
    tmp_lst.append(teacher)

db.session.add_all(tmp_lst)
db.session.commit()
