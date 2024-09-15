from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from .models import User, Question
from .utils import *
from . import db, mail
#using werkzeug because it offers more flexibility and does not limit algorithm to just bcrypt -> it is also usually faster
#using hashlib would create too much unnecessary work


routes = Blueprint('routes', __name__)
#just telling python that this file is a blueprint for storing all the routes


@routes.route('/', methods = ['GET', 'POST'])
@routes.route('/login', methods = ['GET', 'POST'])
def login():
   if request.method == 'POST':
       username = request.form.get('username')
       password = request.form.get('password')


       user = User.query.filter_by(username = username).first()


       if not user:
           #aka user does not exist
           flash('Incorrect username or password', category = 'error')
           return render_template('login.html')
       
       else:
           
           if check_password_hash(user.password, password):
           #comparing the password stored in the user instance/object to the one entered in the form
               flash('Successful Login', category = 'success')
               login_user(user, remember = True)
               
               return redirect(url_for('routes.learn'))
               #redirecting the user to the home page if they are sucessful at logging in
       
   return render_template('login.html')


@routes.route('/sign-up', methods = ['GET', 'POST'])
@routes.route('/create-an-account', methods = ['GET', 'POST'])
def signUp():
   if request.method == 'POST':
       email = request.form.get('email')
       username = request.form.get('username')
       password = request.form.get('password')
       confirmPassword = request.form.get('confirmPassword')

       errors = []


       if not validateEmail(email):
           errors.append('Invalid Email')


       if notUniqueUsername(username):
           errors.append('Username already taken')


       if password != confirmPassword:
           errors.append('Passwords do not match')


       if not validatePassword(password):
           errors.append('Invalid Password')


       if errors:
           for error in errors:
               flash(error, category = 'error')
           return render_template('signUp.html')


       else:
           newUser = User(email = email, username = username, password = generate_password_hash(password), progress = 0)
           
           db.session.add(newUser)
           #adding new user entry
           db.session.commit()
           
           flash('Account created, login to start learning!', category = 'success')
           #provides a confirmation message when account is created successfully
           
           return redirect(url_for('routes.login'))
           #get user to login with their just-created login credentials
       
   return render_template('signUp.html')


@routes.route('/logout')
@login_required
#make sure that you must be logged in to log out
def logout():
   logout_user()
   return redirect(url_for('routes.login'))
   
@routes.route('/forgor-password', methods = ['GET', 'POST'])
def forgorPassword():
   if request.method == 'POST':
       email = request.form.get('email')
       user = User.query.filter_by(email = email).first()
       #checking if the email exists in the database


       if user:
           flash(f'A link to reset your password has been sent to {email}', category = 'success')

           resetToken = generateResetToken(user.email)
           #creating token, which would be saved within the reset link


           msg = Message(subject = 'Luodingo Password Reset', recipients = [email], body = f'Reset password with this link: {url_for(f'routes.resetPassword', token = resetToken, _external = True)}\n\nThis link expires in 1 hour.')
           #_external = True to show the absolute URL, rather than the relative one
           
           mail.send(msg)
           return redirect(url_for('routes.login'))


       else:
           flash(f'{email} is not in the database, sign up to create an account or try again', category = 'error')
           return render_template('forgorPassword.html')


   return render_template('forgorPassword.html')


@routes.route('/reset-password/<token>', methods = ['GET', 'POST'])
def resetPassword(token):
   email = verifyResetToken(token)
   
   if not email:
       flash('The reset link is invalid or has expired', category = 'error')
       return redirect(url_for('routes.login')) 
   
   if request.method == 'POST':
       password = request.form.get('password')
       confirmPassword = request.form.get('confirmPassword')


       errors = []


       if password != confirmPassword:
           errors.append('Passwords do not match')


       if not validatePassword(password):
           errors.append('Invalid Password')


       if errors:
           for error in errors:
               flash(error, category = 'error')
           return render_template('resetPassword.html', token = token)


       else:
           user = User.query.filter_by(email = email).first()


           user.password = generate_password_hash(password)
           db.session.commit()
           flash('Password has been updated', category = 'success')
           
           return redirect(url_for('routes.login'))


   return render_template('resetPassword.html', token = token)


@routes.route('/home', methods = ['GET', 'POST'])
@routes.route('/learn', methods = ['GET', 'POST'])
@login_required
def learn():
    if request.method == 'POST':
        return redirect(url_for('routes.lesson'))
    
    return render_template('learn.html')

@routes.route('/lesson', methods = ['GET', 'POST'])
@login_required
def lesson():
    # lesson = Lesson.query.filter_by(lessonId = lessonId).first()

    # if not lesson:
    #     flash('Lesson could not be found... You will be redirected to the learn page.', category = 'error')
    #     return redirect(url_for('routes.learn'))

    # if request.method == 'POST':
    #     #probably need a few if statements to load the first card of the lesson
    #     return '<h1> Card </h1>'
    
    # else:
    #     return
    
    return '<h1>Question Here!</h1>'

@routes.route('/add-a-question', methods = ['GET', 'POST'])
@login_required
def addQuestion():
    if current_user.email == 'lukz@merciaschool.com':
        #means that only I can add questions right now

        if request.method == 'POST':
            question = request.form.get('question')
            answer = request.form.get('answer')
            questionType = request.form.get('questionType')

            newQuestion = Question(question = question, answer = answer, questionType = questionType, correct = 0, revisit = 0)

            db.session.add(newQuestion)
            db.session.commit()

            flash('Question has been added.', category = 'success')
            return render_template('addQuestion.html')
        
        return render_template('addQuestion.html')
    
    else:
        flash('Access restricted... You will be redirected to the learn page.', category = 'error')
        #need to fix this flash message not showing -> shows up only when the user logs out
        return redirect(url_for('routes.learn'))
    
@routes.route('/question/<questionId>', methods = ['GET', 'POST'])
@login_required
def accessQuestion(questionId):
    question = Question.query.filter_by(id = questionId).first()

    if request.method == 'POST':
        answer = request.form.get('answer')

        if answer == question.answer:
            return True
        
        return False

    else:
        return render_template(f'{question.questionType}.html', question = question)
        #question types can only be: multiple-choice, fill-in-the-blanks, mouse-navigation, keyboard-input            