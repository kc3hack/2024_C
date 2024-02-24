"""
note, PythonのFlaskでデータベースを利用する方法(Flask-SQLAlchemy), 
https://note.com/junyaaa/n/n9eab953c73c9, 2024年2月14日.

起動方法
app.pyがあるdir内で「flask run」をして実行
"""

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os 
import time

from TTS_voicevox_local_api_file_write import TTC_voicevox_local_api_chara #TTS
from Sentenc_Sim import detect_selected_num, detect_yes_or_no #NLP
from GPS_address_distance import GPS_Address_Distance #GPS
from GPT35_turbo_RAG import llm_preparation, llm_communication #LLM

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.todo' #データベース作成のための種類とファイル名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #SQLAlchemyがセッションへの変更を追跡するかどうか

# 文字化け防止
app.config['JSON_AS_ASCII'] = False

#キャッシュを捨てる
app.config['TEMPLATES_AUTO_RELOAD'] = True

#シークレットキー
app.secret_key = 'your_secret_key'

socketio = SocketIO(app)

# 初回のアクセス時に初期化を行うフラグをセットするキー
INITIALIZED_KEY = 'initialized'


db = SQLAlchemy(app) #SQLAlchemyのインスタンスを作成する
#db.init_app(app)

#音声合成キャラクタの初期化
TTS_zundamon_class = TTC_voicevox_local_api_chara(speaker=2)

#CSV GPS知識データ読込みの初期化
GPS_add_dis = GPS_Address_Distance()

"""
データベース
"""
class ToDo(db.Model): #dbのModelを継承したテーブルのクラスを定義する

	id = db.Column(db.Integer, primary_key=True) #primary_key=True ここを主キーとする
	todo = db.Column(db.String(128), nullable=False)


"""
セッションでリスト型を扱う
"""
class SessionList(list):
    def __setitem__(self, i, item):
        super(SessionList, self).__setitem__(i, item)
        session.modified = True


@app.route('/')
def index():
	session.clear()  # 一時的にセッションをクリア
	#print("Session after clear:", session)
	data = ToDo.query.all() #データベースのToDoモデルのデータを全て検索して取得 dataへ格納
	return render_template('todo.html',data=data) #html側でこの変数todoを扱えるようにする


#隠れスポット入力画面
@app.route('/input_spot')
def input_spot():

	session.clear()  # 一時的にセッションをクリア
	#print("Session after clear:", session)

	return render_template('input_spot.html')


#以下追加↓	
#/addのURLへPOSTリクエストがあった場合 (追加と表示)
@app.route('/add', methods=['POST'])
def add():
	todo = request.form['todo'] #ormタグ内のname='todo'からデータを取得して変数todoに割り当てる
	new_todo = ToDo(todo=todo)  #データベースのモデルのToDoクラスをインスタンス化して、引数にキーワードでtodo=todoとして変数new_todoに割り当てる
	db.session.add(new_todo)    #変数new_todoをセッションに追加し
	db.session.commit()         #先程セッションにaddしたデータをデータベースに追加する

	return redirect(url_for('index')) #index関数に紐づけられているルーティングにリダイレクトで転送する

#DBの削除
@app.route('/del_todo/<int:id>') #idというパラメータを@app.routeで定義したときには, 函数の引数にすることを忘れない
def del_todo(id):
	del_data = ToDo.query.filter_by(id=id).first() #特定のidのものを検索して取得
	db.session.delete(del_data) #以下2行で当該データを削除
	db.session.commit()
	return redirect(url_for('index'))


#JSとの操作をまとめて行う
"""
note, PythonのFlaskでCSSやJSを使う, Pythonista3でも可能, 
https://note.com/junyaaa/n/ncbec90fe8cad, 2024年2月15日
"""
@app.route('/javascript_funcs')
def javascript_funcs():
	
    return render_template('js_func.html') #html側でこの変数todoを扱えるようにする


"""
Qiita, たった17行のコードで音声自動文字起こしを実装する
https://qiita.com/kolife/items/a0af7702eef05994fbfb, 2024年2月15日.
"""
#音声認識の1回ごとの繰り返し
@app.route('/js_while_speech_recognition')
def while_speech_recognition():
	
    return render_template('while_speech_recognition.html') #html側でこの変数todoを扱えるようにする



"""
[状態1 selection]
1. 人-->AI 音声で選択させる 

[状態2 confirmation]
2. AI-->人 合成音声で確認する 「○○というスポットやな」

[状態3 overview]
3. AI-->人 そのスポットの概要を教える

[状態4 communication] 
4. 人-->AI スポットのこと(を質問/について雑談)する
5. AI-->人 ユーザの問いかけに返答する
"""

#状態リスト
STATE_LIST = {"selection":1, "confirmation":2, "overview":3, "communication":4}

SESSION_INIT = True

"""
LLM初期化したときのものを保存する変数 golbal変数とする
"""
list_index = ""
hogen_llm = ""
hogen_tag = ""

#/<string:state>
#音声認識の連続的な繰り返し methodを明示しないとmethod not allowed errorになる
@app.route('/loop_speech_recognition',  methods=['POST', 'GET'])
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
				"prefecture":"", #地域
				"kuchikomi_num":0, #口コミ数
				"URL":"", #URL
				"address":"", #住所
				"abstract":"", #概要
				"explanation":"", #説明
				"latitude":"", #緯度
				"longitude":"" #経度
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
				
				Top_10_nearest_spots = GPS_add_dis.get_nearest_spots_by_distance(session['my_latitude'], session['my_longitude'])
				
				#京都府の場合は京都弁になる
				if Top_10_nearest_spots[int(session['selected_spot'])-1][2] == "京都府":
					session['speech_text'] = str(session['selected_spot']) + "番目のスポットにおいでやす"

				#兵庫県の場合は神戸弁になる
				elif Top_10_nearest_spots[int(session['selected_spot'])-1][2] == "兵庫県":
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
				Top_10_nearest_spots = GPS_add_dis.get_nearest_spots_by_distance(session['my_latitude'], session['my_longitude'])
				
				#京都府の場合は京都弁になる
				if Top_10_nearest_spots[int(session['selected_spot'])-1][2] == "京都府":
					session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1][1] + "って名前やし" + Top_10_nearest_spots[int(session['selected_spot'])-1][6] + "感じのスポットにならはるわ"

				#兵庫県の場合は神戸弁になる
				elif Top_10_nearest_spots[int(session['selected_spot'])-1][2] == "兵庫県":
					session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1][1] + "ちゅうところで" + Top_10_nearest_spots[int(session['selected_spot'])-1][6] + "感じのスポットみたいやな"

				#それ以外の場合は大阪弁になる
				else:
					session['speech_text'] = str(session['selected_spot']) + "番目は" + Top_10_nearest_spots[session['selected_spot']-1][1] + "ちゅうところで" + Top_10_nearest_spots[int(session['selected_spot'])-1][6] + "感じのスポットになっとってん"
				
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
				Top_10_nearest_spots = GPS_add_dis.get_nearest_spots_by_distance(session['my_latitude'], session['my_longitude'])
				

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




#ボタンで挙動が変わるもの
@app.route('/map_spot', methods=['POST', 'GET'])
def map_spot_show():
	#session.clear()  # 一時的にセッションをクリア
	#print("Session after clear:", session)

	if request.method == "POST":
		session['my_latitude'] = request.form.get('my_latitude')
		session['my_longitude'] = request.form.get('my_longitude')

		print("自分は今, ")
		print("緯度=" + str(session['my_latitude']) + ", 経度=" + str(session['my_longitude']) + "にいます!")

	return render_template('map_spot.html') #html側でこの変数todoを扱えるようにする


#ボタンで挙動が変わるもの
@app.route('/js_button_text_change')
def button_text_change():
	
    return render_template('change_text_by_button.html') #html側でこの変数todoを扱えるようにする


"""
flaskで音声ファイルを再生する
Wizard Notes, Flask：Webアプリでサーバ上のオーディオファイルを再生・ダウンロード
https://www.wizard-notes.com/entry/python/flask-audiofile
"""
#音声ファイルを再生するためのページの表示
@app.route("/audio_page")
def audio_page():
	audio_changed = 0 # 0:音声ファイルが同じ(同じ内容を話している)
	                  # 1:音声ファイルが異なる(違う内容を話している)

	return render_template("audio_page_loop_button.html", result = audio_changed)


#音声ファイルの置き場
@app.route("/music/<path:filename>")
def audio_page_play(filename):
    return send_from_directory("music", filename)



@app.route('/get_audio')
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


@app.route('/realtime_ajax_map')
def realtime_map_show():
    return render_template('realtime_ajax_map.html')


"""
地図の位置を更新する
"""
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


#Socket入出力
@socketio.on('connect')
def handle_connect():
	print('Client connected')
	send_random_coordinates()
	#start_coordinate_generation()


"""
ランダムに生成した座標を送る
"""
def send_random_coordinates():
	#print("ランダムな緯度経度を作れり")
	for i in range(10):
		Top_10_nearest_spots = GPS_add_dis.get_nearest_spots_by_distance(session['my_latitude'], session['my_longitude'])
	
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
			"kind":          Top_10_nearest_spots[i][0], #種類
			"name":          Top_10_nearest_spots[i][1], #名前
			"prefecture":    Top_10_nearest_spots[i][2], #地域
			"kuchikomi_num": Top_10_nearest_spots[i][3], #口コミ数
			"URL":           Top_10_nearest_spots[i][4], #URL
			"address":       Top_10_nearest_spots[i][5], #住所
			"abstract":      Top_10_nearest_spots[i][6], #概要
			"explanation":   Top_10_nearest_spots[i][7], #説明
			"latitude":      Top_10_nearest_spots[i][9], #緯度
			"longitude":     Top_10_nearest_spots[i][8] #経度
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

	


"""
def start_coordinate_generation():
    def generate_coordinates():
        while True:
            latitude = random.uniform(-90, 90)
            longitude = random.uniform(-180, 180)
            socketio.emit('coordinates', {'latitude': latitude, 'longitude': longitude})
            time.sleep(1)

    thread = Thread(target=generate_coordinates)
    thread.start()
"""

#アプリとDBの初期化
"""
HatenaBlog, クローラー君アウトプットブログ, 
https://seo-crawler.hatenablog.jp/entry/2023/04/19/095314, 2024年2月14日.
"""
def app_db_init(app, db):
    app.app_context().push()
    db.create_all() #データベースを作成する 初回に1回のみ実行



@app.route('/clear_session')
def clear_session():
    session.clear()
    return 'Session cleared!'


if __name__ == '__main__':
	app_db_init(app, db) #データベースを作成する 初回に1回のみ実行
	#app.run(debug=True)  #アプリケーションを毎回実行する
	#socketio.run(app, debug=True)
	socketio.run(app, host='0.0.0.0', port=7000)
	#http://192.168.1.151:5000
	"""
	flask run --host=0.0.0.0 --port=5000
	"""
