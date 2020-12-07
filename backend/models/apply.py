from application.app import db
import datetime


class Apply(db.Model):
    __tablename__ = 'apply'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.Integer)
    is_on = db.Column(db.Boolean)
    apply_user = db.Column(db.Integer)
    apply_time = db.Column(db.DateTime)
    rate = db.Column(db.Float)

    def __init__(self, task, apply_user):
        self.task = task
        self.apply_user = apply_user
        self.apply_time = datetime.datetime.now()
        self.is_on = False
