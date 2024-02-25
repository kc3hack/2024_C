'''
起動方法
app.pyがあるディレクトリで"flask run"を実行
'''

from flask import Flask, redirect, url_for, render_template, flash, request, session, send_file
from flask_login import current_user, login_user, logout_user, login_required
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
import flask_login
from forms import LoginForm, SignUpForm, AddSpotForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pandas
from TTS_voicevox_local_api_file_write import TTC_voicevox_local_api_chara #TTS
import os
from GPT35_turbo_RAG import llm_communication, llm_preparation
import time
from Sentenc_Sim import detect_selected_num
import urllib
import requests
import numpy as np
from geopy.distance import geodesic

#別ファイルだったものを循環importの問題から移動
class GPSAddressDistance:
    def __init__(self) -> None:
        pass

    #地点を追加するときに住所から座標を取得する。エラーがある場合-65535を出して終了(正直戻り値の型変えたくない)
    def addressToChoords(self, address: str):
        makeUri = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
        quote = urllib.parse.quote(address)
        try:
            responce = responce = requests.get(makeUri + quote)
            pos = responce.json()[0]["geometry"]["coordinates"]
            return pos[1], pos[0]
        except Exception as e:
            print(f"住所から座標の取得に失敗しました。<住所：{address}, 例外：({e.__class__.__name__}:{e.args})>")
            return -65535, -65535

    #距離が最も近い10個のスポットを取得する。
    def getNearestSpotByDistance(self, my_lati : float, my_long : float):
        choords = db.session.query(Spot.longitude, Spot.latitude).all()#緯度と経度を選択し取得する。
        distanceList = np.empty(0)
        for choordData in choords:#列を取得
            spotChoordsTuple = (choordData.latitude, choordData.longitude)#列からタプルへの変換
            #print(f"spotChoordTuple > {spotChoordsTuple}")
            myPosTuple = (my_lati, my_long)
            #print(f"myPosTuple > {myPosTuple}")
            distance = geodesic(spotChoordsTuple, myPosTuple).m#距離取得
            #print(f"distance > {distance}")
            distanceList = np.append(distanceList, distance)#距離のリストに追加。
        spotsIndexSortedByDistance = np.argsort(distanceList)[::1]
        top10NearestSpots = []#近い順にインデックス番号を並べるためのリスト。
        for i in range(10):
            allData = db.session.query(Spot).all()#全てのデータモデルを取得する。
            spot = allData[spotsIndexSortedByDistance[i]]#データを引っ張り出し格納
            top10NearestSpots.append(spot)
        return top10NearestSpots

#アプリケーションの初期化処理--------------------
mainapp = Flask(__name__)
mainapp.config.from_object(Config)
socketio = SocketIO(mainapp)
db = SQLAlchemy(mainapp)
#db.init_app(mainapp)
migrate = Migrate(mainapp, db)
login_manager = flask_login.LoginManager()
login_manager.init_app(mainapp)
INITIALIZED_KEY = 'initialized'
TTS_zundamon_class = TTC_voicevox_local_api_chara(speaker=2)
GPS_add_dis = GPSAddressDistance()
#-------------------------------------------
#importlib.import_module("GPSAddressDistance")
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
    session.clear()
    return redirect(url_for('login'))

@mainapp.route('/index')
@login_required
def index():
    session.clear()
    return render_template('index.html', title='Sign In')


STATE_LIST = {"selection":1, "confirmation":2, "overview":3, "communication":4}

SESSION_INIT = True

"""
LLM初期化したときのものを保存する変数 golbal変数とする
"""
list_index = ""
hogen_llm = ""
hogen_tag = ""


@mainapp.route('/loop_speech_recognition', methods = ["GET", "POST"])
@login_required
def loop_speech_recognition():
    global SESSION_INIT
    global list_index, hogen_llm, hogen_tag 


    spot_num = 10


    #global state
    #global reconized_text

    audio_changed = 0 # 0:音声ファイルが同じ(同じ内容を話している)
                      # 1:音声ファイルが異なる(違う内容を話している)

    # 音声ファイルのパス
    file_path = "./music/output.wav"


    # セッションから初期化フラグを取得
    initialized = session.get(INITIALIZED_KEY, False)
    print("Session=", session)

    # 初回アクセス時に初期化
    if not initialized:

        print("initializedされました")
        session[INITIALIZED_KEY] = True
        session['state'] = STATE_LIST['selection']
        session['reconized_text'] = ""
        session['selected_spot'] = 1
        session['isAudioUpdated'] = "再生済" #音声ファイルが更新されたかどうか 0変わらない, 1更新された
        session['speech_text'] = ""

        session['my_latitude'] = 0
        session['my_longitude'] = 0

        session['communication_count'] = 0 #対話回数を保持する

        if os.path.exists(file_path):
            os.remove(file_path)
            print("古いファイルを削除しました")

        session['speech_text'] = "1から10までの好きなスポットを選んでくれへん?"
        TTS_zundamon_class.TTS_main(session['speech_text'], path=file_path) #音声合成をする
        session['isAudioUpdated'] = "未再生"

        #付近の近い10スポット

        """
        0     1     2    3        4    5     6    7     8     9
        種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度
        """
        """
        session['near_spots_kind'] = SessionList([""]*10)          #種類
        session['near_spots_name'] = SessionList([""]*10)          #名前
        session['near_spots_prefecture'] = SessionList([""]*10)    #地域
        session['near_spots_kuchikomi_num'] = SessionList([0]*10)  #口コミ数
        session['near_spots_URL'] = SessionList([""]*10)           #URL
        session['near_spots_address'] = SessionList([""]*10)       #住所
        session['near_spots_abstract'] = SessionList([""]*10)      #概要
        session['near_spots_explanation'] = SessionList([""]*10)   #説明
        session['near_spots_latitude'] = SessionList([0]*10)       #緯度(順序 逆)
        session['near_spots_longitude'] = SessionList([0]*10)      #経度(順序 逆)
        session.modified = True
        """

        for i in range(10):
            session['near_spots' + str(i)] = {
                "kind":"", #種類
                "name":"", #名前
                "prefecture":0, #地域
                "kuchikomi_num":0, #口コミ数
                "URL":"", #URL
                "address":"", #住所
                "abstract":"", #概要
                "explanation":"", #説明
                "latitude":0, #緯度
                "longitude":0 #経度
            }


        

        initialized = True    



    
    #print("session['near_spots']=" + str(session['near_spots']))

    #reconized_text = ""

    
    #POSTのとき音声認識の結果を取得する
    if request.method == 'POST':
        #reconized_text = request.form["endMsg"] 

        if request.form.get("reconized_text") != "":
            session['reconized_text'] = request.form.get("reconized_text")

        """
        POSTを投げなくても発話できるようにする
        """

        #audio_changed = request.form.get("result_text")
        #print("reconized_text=" + str(reconized_text))
        #print("audio_changed=" + str(audio_changed))
        #print("audio_chaged=" + str(audio_changed))
        print("session['isAudioUpdated']=" + str(session['isAudioUpdated']))
        print("session['reconized_text']=" + str(session['reconized_text']))
        print("session['state']=" + str(session['state']))



        
            
        #time.sleep(5)
        #print("音楽ファイルを生成する")

        #以前のファイルがあれば削除する

        #ユーザーに選択させる段階である場合
        if session['state'] == STATE_LIST['selection']:
    

            time.sleep(3)

            if request.form.get("reconized_text") != "":
                session['reconized_text'] = request.form.get("reconized_text")

            try:    
                #成功した上で, 何か話していたら
                if session['reconized_text'] != "":
                    #time.sleep(3)
                    session['state'] = STATE_LIST['confirmation']

                    #return redirect('get_audio')

            except Exception:
                pass

            print("session['state']=" + str(session['state']))

            return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated'], speech_text=session['speech_text']) #html側でこの変数todoを扱えるようにする



        #ユーザーに確認させる段階である場合
        if session['state'] == STATE_LIST['confirmation']:

            if os.path.exists(file_path):
                os.remove(file_path)
                print("古いファイルを削除しました")

            try:    
                session['selected_spot'] = detect_selected_num(session['reconized_text'], spot_num)
                
                print("selected_num=" + str(session['selected_spot']))
                
                Top_10_nearest_spots = GPS_add_dis.getNearestSpotByDistance(session['my_latitude'], session['my_longitude'])
                
                #京都府の場合は京都弁になる
                if Top_10_nearest_spots[int(session['selected_spot'])-1].pref == 0:
                    session['speech_text'] = str(session['selected_spot']) + "番目のスポットにおいでやす"

                #兵庫県の場合は神戸弁になる
                elif Top_10_nearest_spots[int(session['selected_spot'])-1].pref == 2:
                    session['speech_text'] = str(session['selected_spot']) + "番目のスポットにしとう"

                #それ以外の場合は大阪弁になる
                else:
                    session['speech_text'] = str(session['selected_spot']) + "番目のスポットにするんか"
                
                
                TTS_zundamon_class.TTS_main(session['speech_text'], path=file_path) #音声合成をする
                
                session['isAudioUpdated'] = "未再生"
                #time.sleep(4)
                session['state'] = STATE_LIST['overview']

            except Exception:
                pass
            
            return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated'], speech_text=session['speech_text']) #html側でこの変数todoを扱えるようにする




        #概要解説
        if session['state'] == STATE_LIST['overview']:

            if os.path.exists(file_path):
                os.remove(file_path)
                print("古いファイルを削除しました")

            try:    
                print("selected_num=" + str(session['selected_spot']))
                #print("session['near_spots_abstract']=" + str(session['near_spots_abstract']))
                #time.sleep(2)
                #session['speech_text'] = str(session['selected_spot']) + "番目のスポットは" + session['near_spots' + str(['selected_spot'] + 1)]["abstract"] + "感じのスポットやねん"
                Top_10_nearest_spots = GPS_add_dis.getNearestSpotByDistance(session['my_latitude'], session['my_longitude'])
                
                #京都府の場合は京都弁になる
                if Top_10_nearest_spots[int(session['selected_spot'])-1].pref == 0:
                    session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1].name + "って名前やし" + Top_10_nearest_spots[int(session['selected_spot'])-1].overview + "感じのスポットにならはるわ"

                #兵庫県の場合は神戸弁になる
                elif Top_10_nearest_spots[int(session['selected_spot'])-1].pref == 2:
                    session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1].name + "ちゅうところで" + Top_10_nearest_spots[int(session['selected_spot'])-1].overview + "感じのスポットみたいやな"

                #それ以外の場合は大阪弁になる
                else:
                    session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1].name + "ちゅうところで" + Top_10_nearest_spots[int(session['selected_spot'])-1].overview + "感じのスポットになっとってん"
                
                TTS_zundamon_class.TTS_main(session['speech_text'], path=file_path) #音声合成をする
                
                #time.sleep(4)
                
                session['isAudioUpdated'] = "未再生"
                session['state'] = STATE_LIST['communication']

            except Exception:
                pass
            
            return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated'], speech_text=session['speech_text']) #html側でこの変数todoを扱えるようにする


        #対話(具体的な説明)
        if session['state'] == STATE_LIST['communication']:
            

            if os.path.exists(file_path):
                os.remove(file_path)
                print("古いファイルを削除しました")

            try:
                #音声を取得する
                #session['reconized_text'] = request.form.get("reconized_text")
                    
                #GPS情報を取得する
                Top_10_nearest_spots = GPS_add_dis.getNearestSpotByDistance(session['my_latitude'], session['my_longitude'])
                

                if session['communication_count'] == 0:
                    #LLMを初期化する
                    list_index, hogen_llm, hogen_tag = llm_preparation(Top_10_nearest_spots[int(session['selected_spot'])-1])
                    session['communication_count'] = 1
                    

                #質問に対する返答を作成する

                if session['reconized_text'] != "":
                    session['speech_text'] = llm_communication(list_index, hogen_llm, hogen_tag, reconized_text=session['reconized_text'])

                else:
                    session['speech_text'] = "なんか質問はあるん?"


                TTS_zundamon_class.TTS_main(session['speech_text'], path=file_path) #音声合成をする


                session['isAudioUpdated'] = "未再生"
            

            except Exception:
                pass

            return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated'], speech_text=session['speech_text']) #html側でこの変数todoを扱えるようにする




    else:
        return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated'], speech_text=session['speech_text']) #html側でこの変数todoを扱えるようにする

@mainapp.route('/get_audio')
def get_audio():

    
    """
    res = requests.post(
            f"http://127.0.0.1:5000/get_audio",
        )
    """

    #print("res=" + str(res))
    

    #print("get_audio_called")

    # 仮に新しいwavファイルを作成するとします
    # この部分を実際のwavデータ生成ロジックに置き換えてください
    # ここでは例として同一ディレクトリ内のsample.wavを使用しています
    return send_file('./music/output.wav', mimetype='audio/wav')

@socketio.on('update_location')
def handle_update_location(data):
	session['my_latitude'] = data.get('latitude', '')
	session['my_longitude'] = data.get('longitude', '')
	
	print("latitude=" + str(session['my_latitude']))
	print("longitude=" + str(session['my_longitude']))

	"""
	0     1     2    3        4    5     6    7     8     9
	種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度

	口コミ数, URL, 住所 
	"""

	#print("session['near_spots_latitude']")


    # クライアントに処理結果をブロードキャスト
	socketio.emit('location_processed', {'result': 'Success'})


@socketio.on('connect')
def handle_connect():
    print('Client Connected')
    send_random_coordinates()

def send_random_coordinates():
    #print("ランダムな緯度経度を作れり")
    for i in range(10):
        Top_10_nearest_spots = GPS_add_dis.getNearestSpotByDistance(session['my_latitude'], session['my_longitude'])
    
        """
        session['near_spots_kind'][i] = Top_10_nearest_spots[i][0] #種類
        session['near_spots_name'][i] = Top_10_nearest_spots[i][1] #名前
        session['near_spots_prefecture'][i] = Top_10_nearest_spots[i][2]   #地域
        
        session['near_spots_kuchikomi_num'][i] = int(Top_10_nearest_spots[i][3]) #口コミ数
        session['near_spots_URL'][i] = Top_10_nearest_spots[i][4]         #URL
        
        session['near_spots_address'][i] = Top_10_nearest_spots[i][5]     #住所
        session['near_spots_abstract'][i] = Top_10_nearest_spots[i][6]    #概要
        session['near_spots_explanation'][i] = Top_10_nearest_spots[i][7]   #説明

        session['near_spots_latitude'][i] = float(Top_10_nearest_spots[i][9])
        session['near_spots_longitude'][i] = float(Top_10_nearest_spots[i][8])
        """

        
        session['near_spots' + str(i)] = {
            "kind":          Top_10_nearest_spots[i].type, #種類
            "name":          Top_10_nearest_spots[i].name, #名前
            "prefecture":    Top_10_nearest_spots[i].pref, #地域
            "kuchikomi_num": 0, #口コミ数
            "URL":           Top_10_nearest_spots[i].jaranUrl, #URL
            "address":       Top_10_nearest_spots[i].address, #住所
            "abstract":      Top_10_nearest_spots[i].overview, #概要
            "explanation":   Top_10_nearest_spots[i].detail, #説明
            "latitude":      Top_10_nearest_spots[i].latitude, #緯度
            "longitude":     Top_10_nearest_spots[i].longitude #経度
        }

    
        """
        socketio.emit('coordinates', {'num': i+1, 
                                    'name': session['near_spots_name'][i], 
                                    'address': session['near_spots_address'][i], 
                                    'abstract': session['near_spots_abstract'][i], 
                                    'latitude': session['near_spots_latitude'][i], 
                                    'longitude': session['near_spots_longitude'][i]})
        """
        socketio.emit('coordinates', {'num': i+1, 
                                    'name': session['near_spots' + str(i)]["name"], 
                                    'address': session['near_spots' + str(i)]["address"], 
                                    'abstract': session['near_spots' + str(i)]["abstract"], 
                                    'latitude': session['near_spots' + str(i)]["latitude"], 
                                    'longitude': session['near_spots' + str(i)]["longitude"]})
                        

        #print("session_in_socket=")
        #print(session)

    session.modified = True


@mainapp.route('/map')

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
    socketio.run(mainapp, host="0.0.0.0", port=8100)