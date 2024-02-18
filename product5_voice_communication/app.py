"""
note, PythonのFlaskでデータベースを利用する方法(Flask-SQLAlchemy), 
https://note.com/junyaaa/n/n9eab953c73c9, 2024年2月14日.

起動方法
app.pyがあるdir内で「flask run」をして実行
"""

from sre_parse import State
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, session
from flask_sqlalchemy import SQLAlchemy
import os 
import time

from TTS_voicevox_local_api_file_write import TTC_voicevox_local_api_chara
from Sentenc_Sim import detect_selected_num, detect_yes_or_no



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.todo' #データベース作成のための種類とファイル名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #SQLAlchemyがセッションへの変更を追跡するかどうか

# 文字化け防止
app.config['JSON_AS_ASCII'] = False

#キャッシュを捨てる
app.config['TEMPLATES_AUTO_RELOAD'] = True

#シークレットキー
app.secret_key = 'your_secret_key'
# 初回のアクセス時に初期化を行うフラグをセットするキー
INITIALIZED_KEY = 'initialized'


db = SQLAlchemy(app) #SQLAlchemyのインスタンスを作成する
#db.init_app(app)

#音声合成キャラクタの初期化
TTS_zundamon_class = TTC_voicevox_local_api_chara(speaker=2)


class ToDo(db.Model): #dbのModelを継承したテーブルのクラスを定義する

	id = db.Column(db.Integer, primary_key=True) #primary_key=True ここを主キーとする
	todo = db.Column(db.String(128), nullable=False)


@app.route('/')
def index():
    data = ToDo.query.all() #データベースのToDoモデルのデータを全て検索して取得 dataへ格納
	
    return render_template('todo.html',data=data) #html側でこの変数todoを扱えるようにする


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


#/<string:state>
#音声認識の連続的な繰り返し methodを明示しないとmethod not allowed errorになる
@app.route('/loop_speech_recognition',  methods=['POST', 'GET'])
def loop_speech_recognition():

	spot_num = 10


	#global state
	#global reconized_text

	audio_changed = 0 # 0:音声ファイルが同じ(同じ内容を話している)
	                  # 1:音声ファイルが異なる(違う内容を話している)

	file_path = "./music/output.wav"

	session.clear()  # 一時的にセッションをクリア
	print("Session after clear:", session)

	# セッションから初期化フラグを取得
	initialized = session.get(INITIALIZED_KEY, False)
	print("Session=", session)

    # 初回アクセス時に初期化
	if not initialized:
		session[INITIALIZED_KEY] = True
		session['state'] = STATE_LIST['selection']
		session['reconized_text'] = ""
		session['selected_spot'] = 1
		session['isAudioUpdated'] = "再生済" #音声ファイルが更新されたかどうか 0変わらない, 1更新された
		initialized = True	

		"""
		POSTを投げなくても発話できるようにする
		"""
		if os.path.exists(file_path):
			os.remove(file_path)
			print("古いファイルを削除しました")

		speech_text = "1から10までの好きなスポットを選んでくれへん?"
		TTS_zundamon_class.TTS_main(speech_text, path=file_path) #音声合成をする
		session['isAudioUpdated'] = "未再生"

	


	#reconized_text = ""

	
	#POSTのとき音声認識の結果を取得する
	if request.method == 'POST':
		#reconized_text = request.form["endMsg"] 
		session['reconized_text'] = request.form.get("reconized_text")
		audio_changed = request.form.get("result_text")
		print("audio_changed=" + str(audio_changed))
		#print("reconized_text=" + str(reconized_text))
		#print("audio_changed=" + str(audio_changed))
		print("audio_chaged=" + str(audio_changed))
		print("session['isAudioUpdated']=" + str(session['isAudioUpdated']))
		print("session['reconized_text']=" + str(session['reconized_text']))
		print("session['state']=" + str(session['state']))



		
		try:	
			#time.sleep(5)
			#print("音楽ファイルを生成する")

			#以前のファイルがあれば削除する

			#ユーザーに選択させる段階である場合
			if session['state'] == STATE_LIST['selection']:

				try:	
					#成功した上で, 何か話していたら
					if session['reconized_text'] != "":
						#time.sleep(3)
						session['state'] = STATE_LIST['confirmation']

						#return redirect('get_audio')

				except Exception:
					pass



			#ユーザーに確認させる段階である場合
			if session['state'] == STATE_LIST['confirmation']:

				if os.path.exists(file_path):
					os.remove(file_path)
					print("古いファイルを削除しました")

				try:	
					session['selected_spot'] = detect_selected_num(session['reconized_text'], spot_num)
					time.sleep(2)
					print("selected_num=" + str(session['selected_spot']))
					
					speech_text = str(session['selected_spot']) + "番目について解説するわ"
					TTS_zundamon_class.TTS_main(speech_text, path=file_path) #音声合成をする
					time.sleep(1)
					session['isAudioUpdated'] = "未再生"
					time.sleep(5)
					session['state'] = STATE_LIST['overview']

				except Exception:
					pass


			#概要解説
			if session['state'] == STATE_LIST['overview']:

				if os.path.exists(file_path):
					os.remove(file_path)
					print("古いファイルを削除しました")

				try:	
					print("selected_num=" + str(session['selected_spot']))
					speech_text = str(session['selected_spot']) + "番目のスポットおもろいスポットがあるねん"
					TTS_zundamon_class.TTS_main(speech_text, path=file_path) #音声合成をする
					time.sleep(1)
					session['isAudioUpdated'] = "未再生"
					time.sleep(5)

				except Exception:
					pass


			#ファイルが新しく生成されるまで待つ
			#while not os.path.isfile(file_path):
			#	print("生成まち")
			#pass

		except Exception:
			print(Exception)

		audio_changed = 1
		

		#print("音楽ファイルを再生する")

	else:
		audio_changed = 0


	#return redirect(url_for('loop_speech_recognition', state="selection", audio_chaged=audio_changed))	
	#return render_template('loop_speech_recognition.html', audio_chaged=audio_changed, state="selection") #html側でこの変数todoを扱えるようにする
	return render_template('loop_speech_recognition.html', audio_chaged=session['isAudioUpdated']) #html側でこの変数todoを扱えるようにする



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
	app.run(debug=True)  #アプリケーションを毎回実行する
