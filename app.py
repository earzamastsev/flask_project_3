from flask import Flask
from flask import render_template
from flask import request as req
import json
import random
from os import path
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    about = db.Column(db.String(2048))
    picture = db.Column(db.String(64))
    rating = db.Column(db.Float)
    price = db.Column(db.Integer)
    goals = db.Column(db.String(255))
    free = db.Column(db.String(1024))
    booking = db.relationship('Booking', back_populates='teacher')


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    clientWeekday = db.Column(db.String(64))
    clientTime = db.Column(db.String(8))
    clientTeacher = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    clientName = db.Column(db.String(255))
    clientPhone = db.Column(db.String(255))
    teacher = db.relationship('Teacher', back_populates='booking')


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(255))
    time = db.Column(db.String(8))
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))


# ==== start preparing data and loading MOSK-data ====
weekdays = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
    "sat": "Суббота",
    "sun": "Воскресенье"
}
goals = {"travel": "Для путешествий", "study": "Для учебы", "work": "Для работы", "relocate": "Для переезда"}


@app.route('/')
def index():
    teachers_for_index = random.sample(teachers, 6)
    print(teachers_for_index)
    return render_template('index.html', teachers=teachers_for_index, goals=goals)


@app.route('/all/')
def all():
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal>/')
def goal(goal):
    goals_teacher = []
    for teacher in teachers:
        if goal in teacher.goals:
            goals_teacher.append(teacher)
    return render_template('goal.html', goals=goals, goal=goal, teachers=goals_teacher)


@app.route('/profiles/<teacher_id>/')
def profile(teacher_id):
    for teacher in teachers:
        if teacher.id == int(teacher_id):
            break
    return render_template('profile.html', goals=goals, teacher=teacher, weekdays=weekdays)


@app.route('/request/')
def request():
    return render_template('request.html')


@app.route('/request_done/', methods=['POST'])
def request_done():
    dict_request = {}
    dict_request['goal'] = req.form.get('goal')
    dict_request['time'] = req.form.get('time')
    dict_request['name'] = req.form.get('name')
    dict_request['phone'] = req.form.get('phone')

    write_json('request.json', dict_request)

    return render_template('request_done.html', data=dict_request, goals=goals)


@app.route('/booking/<teacher_id>/<day>/<time>/')
def booking(teacher_id, day, time):
    for teacher in teachers:
        if teacher.id == int(teacher_id):
            break
    return render_template('booking.html', teacher=teacher, weekdays=weekdays, day=day, time=time)


@app.route('/booking_done/', methods=['POST'])
def booking_done():
    dict_request = {}
    dict_request['clientWeekday'] = req.form.get('clientWeekday')
    dict_request['clientTime'] = req.form.get('clientTime')
    dict_request['clientTeacher'] = req.form.get('clientTeacher')
    dict_request['clientName'] = req.form.get('clientName')
    dict_request['clientPhone'] = req.form.get('clientPhone')

    write_json('booking.json', dict_request)

    return render_template('booking_done.html', data=dict_request, day=weekdays[dict_request['clientWeekday']])


if __name__ == "__main__":
    teachers = db.session.query(Teacher).all()
    app.run()
