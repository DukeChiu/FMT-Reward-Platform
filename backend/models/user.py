from application.app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), primary_key=True)
    pwd = db.Column(db.String(50))
    username = db.Column(db.String(30))
    is_on = db.Column(db.Boolean)
    icon = db.Column(db.String(100))
    rate = db.Column(db.Float)

    def __init__(self, email, pwd, username, is_on, icon):
        self.email = email
        self.pwd = pwd
        self.username = username
        self.is_on = is_on
        self.icon = icon

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'rate': '暂无评价' if self.rate == -1 or self.rate is None else self.rate,
            'icon': self.icon
        }