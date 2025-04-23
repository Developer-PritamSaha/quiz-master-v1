from ..db_base import db
from flask_security import UserMixin, RoleMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    scores = db.relationship('Scores', backref='user', cascade="all, delete-orphan")
    user_data = db.relationship('User_Data', backref='user', cascade="all, delete-orphan")

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)

class Roles_Users(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)  

class User_Data(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)  
    full_name = db.Column(db.String(80), nullable=False)
    qualification = db.Column(db.LargeBinary, nullable=False)
    dob = db.Column(db.Date, nullable=False)
 