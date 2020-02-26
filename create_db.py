from models import db, Teacher, Request, Booking
from app import teachers
import json

db.create_all()

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