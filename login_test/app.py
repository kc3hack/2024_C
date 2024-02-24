'''
起動方法
app.pyがあるディレクトリで"flask run"を実行
'''

from flask import Flask, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from config import Config
from flask_sqlalchemy import SQLAlchemy
import flask_sqlalchemy
from flask_migrate import Migrate
import flask_login
from forms import LoginForm, SignUpForm, AddSpotForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pandas

mainapp = Flask(__name__)
mainapp.config.from_object(Config)
db = SQLAlchemy(mainapp)
migrate = Migrate(mainapp, db)
login_manager = flask_login.LoginManager()
login_manager.init_app(mainapp)

#近くのスポットを抽出(まだ未実装)
def getNearbySpots(longnitude, latitude):
    pass

#じゃらんのデータを抽出(データが追加されていない時に実行)
fileDataFmt = "dataToImport/utf8d/include_data_activity" #csvファイルがあるフォルダ参照
dataExtention = ".csv"
def convert_csv_data_to_db(doCommit = False):
    for i in range(1, 6): #全てのCSVに対して
        data = pandas.read_csv(fileDataFmt + str(i) + dataExtention, header=None) #Csv読み込み
        for d in data.values:
            newSpot = Spot()#隠れスポット定義
            try:
                #隠れスポットの情報を追加。種類については未記載のため-1とする。
                #緯度・経度情報は不正な値が入らないよう数値かチェックする
                newSpot = Spot(name=d[1], overview = d[6], type = -1, detail = d[7], longitude = float(d[8]), latitude = float(d[9]), jaranUrl = d[4], address = d[5])
            except Exception as e:
                #フォーマットに問題があるデータはエラー出力をしてスキップする。
                print("Data Passed")
                print(d)
                print(f"Reason < {e.__class__.__name__} : {e.args}>")
                continue
            prefName = d[2]
            #地域の文字列情報をDB用の数値に変換
            if prefName == '京都':
                newSpot.pref = 0
            elif prefName == '大阪':
                newSpot.pref = 1
            elif prefName == '兵庫':
                newSpot.pref = 2
            elif prefName == '滋賀':
                newSpot.pref = 3
            elif prefName == '奈良':
                newSpot.pref = 4
            elif prefName == '和歌山':
                newSpot.pref = 5
            else:
                newSpot.pref = -1
            if (doCommit):
                Spot.query.session.add(newSpot)  #スポットの情報を追加
                Spot.query.session.commit()  #DBに反映

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
    pref = db.Column(db.Integer)#隠れスポットが所在する県　#0 : 京都, 1 : 大阪, 2 : 兵庫, 3 : 滋賀, 4:奈良, 5:和歌山
    overview = db.Column(db.String(128), index=True) #隠れスポットの概要
    detail = db.Column(db.Text) #隠れスポットの詳細
    latitude = db.Column(db.Float, index=True)#緯度
    longitude = db.Column(db.Float, index=True)#経度
    jaranUrl = db.Column(db.String(100), index=True)#じゃらんから追加した場合のURL  ユーザー追加の場合Noneになる
    address = db.Column(db.String(100), index=True) #隠れスポット住所

    def __repr__(self):
        return f'Spot {self.name}'

class RawSpot:
    id = 0
    name = ''
    type = -1
    pref = -1
    overview = ""
    detail = ""
    longitude = 0
    latitude = 0
    jaranUrl = ""
    address = ""

#有名スポット(隠れスポットから除外されたスポット)のデータベースモデル
class RejectedSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    detail = db.Column(db.Text)
    overview = db.Column(db.String(128), index=True)
    longitude = db.Column(db.Float, index=True)
    latitude = db.Column(db.Float, index=True)

    def __repr__(self):
        return f'<RejectedSpot  {self.name}>'

@mainapp.route('/', methods=['GET', 'POST'])
@mainapp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('map'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('map'))
    return render_template('login.html', title='Sign In', form=form)

@mainapp.route('/signup', methods=['GET', 'POST'])
def signup():#サインアップ実装
    if current_user.is_authenticated:
        return redirect(url_for('map'))
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
    return render_template("map.html", cssMode = "map")

#隠れスポット追加の実装
@mainapp.route('/addspot', methods = ['GET', 'POST'])
@login_required
def add_spot():
    form = AddSpotForm()
    if form.validate_on_submit() and request.method == "POST":
        newSpot = Spot(name = form.spot_name.data, longitude = form.longitude.data, 
                       latitude = form.latitude.data, overview = form.spot_overview.data,
                       detail = form.spot_detail.data, type = int(form.spot_type.data),
                       pref = int(form.spot_place.data))
        Spot.query.session.add(newSpot)
        Spot.query.session.commit()
        return redirect(url_for("map"))
    return render_template('addSpot.html', form = form, cssMode = "add_spot")

if __name__ == "__main__":
    mainapp.run(debug=True, port=8000, host="0.0.0.0")