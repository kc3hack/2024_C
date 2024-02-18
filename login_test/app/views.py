from flask import flash, redirect, url_for, render_template
from flask_login import (
         current_user, login_user, logout_user, login_required
     )
from app import app
from app.models import User
from app.forms import LoginForm
from app.forms import SignUpForm

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():#サインアップ実装
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user is None:
            flash('This User is present.')
            return redirect(url_for('signup'))
        newUser = User(username=form.username.data, email = form.email.data)
        newUser.set_password(form.password.data)
        User.query.session.add(newUser)
        User.query.session.commit()
        login_user(newUser)
        return redirect(url_for('index'))
    return render_template('signup.html', title = 'Sign Up', form=form)

@app.route('/logut')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Sign In')

@app.route('/communication')
@login_required
def communication():
    return 'aaaaaa'

@app.route('/map')
@login_required
def map():
    return 'map'

@app.route('/addspot')
@login_required
def add_spot():
    return 'KakureSpot'
