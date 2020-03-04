from flask import Flask
from flask import render_template, redirect, url_for, abort
from flask import request as req
import json
import random
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Regexp, Required

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)


# ==== Creating Models and relationship one-to-many for SQLAlchemy ====
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
    clientPhone = db.Column(db.String(255), nullable=False, unique=True)
    teacher = db.relationship('Teacher', back_populates='booking')


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False, unique=True)


# ==== Creating WTForms classes for booking and request views ====
class BookingForm(FlaskForm):
    clientWeekday = HiddenField(validators=[DataRequired()])
    clientTime = HiddenField(validators=[DataRequired()])
    clientName = StringField('Вас зовут', validators=[DataRequired(message='Поле не должно быть пустым.'), \
                                                      Regexp("^[A-zА-яЁё]+$", message='Имя дожно состоять из букв.')])
    clientPhone = StringField('Ваш телефон (в формате 89111234567)', validators=[
        Regexp('^((\+7|7|8)+([0-9]){10})$', message='Неверный формат телефонного номера.')])
    teacher = HiddenField(validators=[DataRequired()])


class RequestForm(FlaskForm):
    goal = RadioField(
        'Какая цель занятий?',
        choices=[('travel', 'Для путешествий'), ('study', 'Для учебы'), ('work', 'Для работы'),
                 ('relocate', 'Для переезда')], default='travel',
        validators=[DataRequired(message='Укажите какая цель занятий.')])
    time = RadioField(
        'Сколько времени есть?',
        choices=[('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов в неделю'), ('5-7', '5-7 часов в неделю'),
                 ('7-10', '7-10 часов в неделю')], default='1-2',
        validators=[DataRequired(message='Укажите сколько времени готовы посвещать занятиям.')])
    name = StringField('Вас зовут', validators=[DataRequired(message='Поле не должно быть пустым.'), \
                                                Regexp("^[A-zА-яЁё]+$", message='Имя дожно состоять из букв.')])
    phone = StringField('Ваш телефон (в формате 89111234567)',
                        validators=[Regexp('^((\+7|7|8)+([0-9]){10})$', message='Неверный формат телефонного номера.')])


# ==== preparing data ====
weekdays = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
    "sat": "Суббота",
    "sun": "Воскресенье"
}
goals = {"travel": ["Для путешествий", "⛱"], "study": ["Для учебы", "🏫"], "work": ["Для работы", "🏢"],
         "relocate": ["Для переезда", "🚜"]}


# ==== views for URLs ====
@app.route('/')
def index():
    teachers_for_index = random.sample(teachers, 6)
    return render_template('index.html', teachers=teachers_for_index, goals=goals)


@app.route('/all/')
def all():
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal>/')
def goal(goal):
    if goal in goals.keys():
        goals_teacher = []
        for teacher in teachers:
            if goal in json.loads(teacher.goals):
                goals_teacher.append(teacher)
        return render_template('goal.html', goals=goals, goal=goal, teachers=goals_teacher)
    return abort(404, description='Запрошенная цель обучения отсутствует')


@app.route('/profiles/<teacher_id>/', )
def profile(teacher_id):
    teacher = db.session.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher:
        teacher.free = json.loads(teacher.free)
        teacher.goals = json.loads(teacher.goals)
        return render_template('profile.html', goals=goals, teacher=teacher, weekdays=weekdays)
    return abort(404, description='Запрошенный преподователь не найден')


@app.route('/request/', methods=['POST', 'GET'])
def request():
    form = RequestForm()
    if form.validate_on_submit():
        request = Request()
        form.populate_obj(request)
        db.session.add(request)
        db.session.commit()
        return render_template('request_done.html', data=form, goals=goals)
    return render_template('request.html', form=form)


@app.route('/booking/<teacher_id>/<day>/<time>/', methods=['POST', 'GET'])
def booking(teacher_id, day, time):
    form = BookingForm()
    if form.validate_on_submit():
        form.teacher.data = db.session.query(Teacher).get(form.teacher.data)
        booking = Booking()
        form.populate_obj(booking)
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', data=form, day=weekdays[form.clientWeekday.data])
    teacher = db.session.query(Teacher).get(teacher_id)
    if teacher and (day in weekdays.keys()) and int(time) in range(8, 23, 1):
        return render_template('booking.html', form=form, teacher=teacher, weekdays=weekdays, day=day, time=time)
    else:
        return abort(404, description='Параметры бронирования указаны не верно')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error)

# ==== starting app ====
if __name__ == "__main__":
    teachers = db.session.query(Teacher).all()
    app.run()
