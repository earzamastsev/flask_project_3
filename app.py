from flask import Flask
from flask import render_template
from flask import request as req
from flask import redirect
import json
import random
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, HiddenField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)


# ==== Creating Models and relationship one-to-many for SQLAlchemy ====
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


# ==== Creating WTForms classes for booking and request views ====
class BookingForm(FlaskForm):
    clientWeekday = HiddenField(validators=[DataRequired()])
    clientTime = HiddenField(validators=[DataRequired()])
    clientName = StringField('Вас зовут', validators=[DataRequired()])
    clientPhone = StringField('Ваш телефон', validators=[DataRequired()])
    teacher = HiddenField(validators=[DataRequired()])


class RequestForm(FlaskForm):
    goal = RadioField(
        'Какая цель занятий?',
        choices=[('travel', 'Для путешествий'), ('study', 'Для учебы'), ('work', 'Для работы'),
                 ('relocate', 'Для переезда')],
        validators=[DataRequired()])
    time = RadioField(
        'Сколько времени есть?',
        choices=[('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов в неделю'), ('5-7', '5-7 часов в неделю'),
                 ('7-10', '7-10 часов в неделю')],
        validators=[DataRequired()])
    name = StringField('Вас зовут', validators=[DataRequired()])
    phone = StringField('Ваш телефон', validators=[DataRequired()])


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
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=['POST'])
def request_done():
    form = RequestForm()
    if form.validate_on_submit():
        return render_template('request_done.html', data=form, goals=goals)
    else:
        return form.errors


@app.route('/booking/<teacher_id>/<day>/<time>/')
def booking(teacher_id, day, time):
    for teacher in teachers:
        if teacher.id == int(teacher_id):
            form = BookingForm()
            return render_template('booking.html', form=form, teacher=teacher, weekdays=weekdays, day=day, time=time)


@app.route('/booking_done/', methods=['POST'])
def booking_done():
    form = BookingForm()
    if form.validate_on_submit():
        return render_template('booking_done.html', data=form, day=weekdays[form.clientWeekday.data])
    else:
        return form.errors


if __name__ == "__main__":
    teachers = db.session.query(Teacher).all()
    app.run()