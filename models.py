""" Models for Feedback app """
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """Create a User model"""

    __tablename__ = "users"

    username = db.Column(db.String(20), unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    # feedbacks = db.relationship('Feedback', cascade='all, delete', passive_deletes=True)

    def get_full_name(self):
        """ Get the user full name """
        return f"{self.first_name} {self.last_name}"

    full_name = property(
        fget = get_full_name
    )

    def __repr__(self):
        """ Show info about User """
        u = self
        return f"<User - Username: {u.username} Full_Name: {u.full_name}>"

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """ Register user w/hashed password & return user """

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """
        Validate that user exists & password is correct
        Return user if valid; else return False
        """

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False


class Feedback(db.Model):
    """Create a Feedback model"""

    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username', ondelete='CASCADE'))
    
    users = db.relationship('User', backref='feedbacks')