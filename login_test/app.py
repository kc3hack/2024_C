from flask import Flask, redirect, url_for, render_template, flash
from flask_login import current_user, login_user, logout_user, login_required
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_login
from forms import LoginForm, SignUpForm, AddSpotForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


mainapp = Flask(__name__)
mainapp.config.from_object(Config)
db = SQLAlchemy(mainapp)
migrate = Migrate(mainapp, db)
login_manager = flask_login.LoginManager()
login_manager.init_app(mainapp)

#近くのスポットを抽出(まだ未実装)
def getNearbySpots(longnitude, latitude):
    pass

class User(UserMixin, db.Model):#ユーザーモデル
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#隠れスポットのデータベースモデル
class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True) #固有ID
    name = db.Column(db.String(128), index=True) #隠れスポットの名前(なるべく正式名称で入れてもらう)
    type= db.Column(db.Integer)#隠れスポットの種類
    pref = db.Column(db.Integer)#隠れスポットが所在する県　#0 : 京都 1 : 神戸 2 : 大阪 3 : その他
    overview = db.Column(db.String(128), index=True)
    detail = db.Column(db.Text) #隠れスポットの概要
    longitude = db.Column(db.Float, index=True)#緯度
    latitude = db.Column(db.Float, index=True)#経度

    def __repr__(self):
        return f'Spot {self.spotname}'

#有名スポット(隠れスポットから除外されたスポット)のデータベースモデル
class RejectedSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    detail = db.Column(db.Text)
    overview = db.Column(db.String(128), index=True)
    longnitude = db.Column(db.Float, index=True)
    latitude = db.Column(db.Float, index=True)

    def __repr__(self):
        return f'<RejectedSpot  {self.name}>'

@mainapp.route('/', methods=['GET', 'POST'])
@mainapp.route('/login', methods=['GET', 'POST'])
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

@mainapp.route('/signup', methods=['GET', 'POST'])
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
        return redirect(url_for('add_spot'))
    return render_template('signup.html', title = 'Sign Up', form=form)

@mainapp.route('/logut')
def logout():
    logout_user()
    return redirect(url_for('login'))

@mainapp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Sign In')

@mainapp.route('/communication')
@login_required
def communication():
    return 'aaaaaa'

@mainapp.route('/map')
@login_required
def map():
    return 'map'

#隠れスポット追加の実装
@mainapp.route('/addspot', methods = ['GET', 'POST'])
@login_required
def add_spot():
    form = AddSpotForm()
    if form.validate_on_submit():
        newSpot = Spot(name = form.spot_name.data, longitude = form.longnitude.data, 
                       latitude = form.latitude.data, overview = form.spot_overview.data,
                       detail = form.spot_detail.data, type = int(form.spot_type.data),
                       pref = int(form.spot_place.data))
        Spot.query.session.add(newSpot)
        Spot.query.session.commit()
        return redirect(url_for("index"))
    return render_template('addSpot.html', form = form)

if __name__ == "__main__":
    mainapp.run(debug=True, port=8000)