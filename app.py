from flask import Flask
from flask import render_template
from flask import request as req
import json
import random
from os import path
from data import goals, teachers

app = Flask(__name__)
app.config['DEBUG'] = True

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

# sampling free-time
for teacher in teachers:
    for day, value in teacher['free'].items():
        for time in value:
            value[time] = bool(random.choices([0, 1], weights=[4, 1])[0])

# goals = {"travel": "Для путешествий", "study": "Для учебы", "work": "Для работы", "relocate": "Для переезда"}
#
# with open('teachers.json', 'r') as f:
#     teachers = json.load(f)
# ==== end loading MOSK-data ====

# function for working with JSON-data (store requests and booking)
def write_json(filename: str, dict_data: dict):
    if path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        data.append(dict_data)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        tmp_ = []
        tmp_.append(dict_data)
        with open(filename, 'w') as f:
            json.dump(tmp_, f, indent=4)

@app.route('/')
def index():
    teachers_for_index = random.sample(teachers, 6)
    return render_template('index.html', teachers=teachers_for_index, goals=goals)

@app.route('/all/')
def all():
    return render_template('index.html', teachers=teachers, goals=goals)

@app.route('/goals/<goal>/')
def goal(goal):
    goals_teacher = []
    for teacher in teachers:
        if goal in teacher['goals']:
            goals_teacher.append(teacher)
    return render_template('goal.html', goals=goals, goal=goal, teachers=goals_teacher)

@app.route('/profiles/<teacher_id>/')
def profile(teacher_id):
    for teacher in teachers:
        if teacher['id'] == int(teacher_id):
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
        if teacher['id'] == int(teacher_id):
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
    app.run()
