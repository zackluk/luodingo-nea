import re
#using regular expressions for validation
from .models import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app


def validateEmail(email):
   return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
   #bool() to convert the output value into boolean, which makes it much easier


def validatePassword(password):
   return bool(re.match(r"""^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};':",.<>?`~\\|/-]).{8,}$""", password))
   #had to use triple quotes because regex pattern included both '' and ""


def notUniqueUsername(createUsername):
   user = User.query.filter_by(username = createUsername).first()
   return user
   #returns true which means username taken in is not unique because it already exists in the database


def generateResetToken(email):
   return URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(email)


def verifyResetToken(token, expiration = 3600):
   serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

   try:
       email = serialiser.loads(token, max_age = expiration)


   except (SignatureExpired, BadSignature):
       return None
   
   return email