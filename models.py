from app import db

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