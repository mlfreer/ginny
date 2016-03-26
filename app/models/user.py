from app import db
from flask.ext.security import UserMixin
from sqlalchemy_utils import EmailType

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EmailType, index=True, unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    active = db.Column(db.Boolean(), default=lambda: True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.email)
