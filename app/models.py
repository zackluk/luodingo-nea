from . import db, migrate
#. refers to current file, aka app
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    #defining schema
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), nullable = False, unique = True)
    username = db.Column(db.String(64), nullable = False, unique = True)
    password = db.Column(db.String(64), nullable = False)
    progress = db.Column(db.Integer, nullable = False)
    #progress should be set to 0 when creating an instance
    #username and email set to unique in the table, as they should be unique values

    def __repr__(self):
        #repr function just to check all the fields of a record
        return f'{self.id} {self.email} {self.username} {self.password} {self.progress}'
    
class Lesson(db.Model):
    #Renamed deck -> lesson, as I felt that it made more sense
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key = True)
    deck = db.Column(JSON, nullable = False)
    #using a JSON field to store the list, as python lists are not directly supported to be a Python attribute on sqlalchemy

    def __repr__(self):
        return f'{self.id} {self.deck}'

class Question(db.Model):
    #Renamed card -> question, also just because it is more suitable
    __tablename__ = 'questions'

    #defining schema
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    questionType = db.Column(db.String(32), nullable=False)
    correct = db.Column(db.Integer, nullable=False)
    revisit = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.id} {self.question} {self.answer} {self.questionType} {self.correct} {self.revisit}'