from application.app import db
import datetime
import time

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    disc = db.Column(db.String(500))
    price = db.Column(db.DECIMAL(20, 6), nullable=False)
    contact = db.Column(db.String(100))
    initiator = db.Column(db.Integer)
    task_time = db.Column(db.DateTime)

    def __init__(self, title: str, disc: str, price: str, contact: str, initiator: str):
        self.title = title
        self.disc = disc
        self.price = price
        self.contact = contact
        self.initiator = initiator
        self.task_time = datetime.datetime.now()

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'disc': self.disc,
            'price': self.price,
            'initiator': self.initiator,
            'time': self.task_time,
        }

    def to_json_secret(self):
        return {
            'title': self.title,
            'disc': self.disc,
            'price': self.price,
            'initiator': self.initiator,
            'time': self.task_time,
            'contact': self.contact
        }


# print(datetime.datetime.now())