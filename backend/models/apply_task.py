from application.app import db


class ApplyTask(db.Model):
    __tablename__ = 'apply_task'
    task_id = db.Column(db.Integer, primary_key=True)
    initiator = db.Column(db.Integer)
    apply_user = db.Column(db.Integer)
    rate = db.Column(db.Float)
    price = db.Column(db.DECIMAL(20, 6))
