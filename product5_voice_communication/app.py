"""
note, PythonのFlaskでデータベースを利用する方法(Flask-SQLAlchemy), 
https://note.com/junyaaa/n/n9eab953c73c9, 2024年2月14日.

起動方法
app.pyがあるdir内で「flask run」をして実行
"""

from unittest import result
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.todo' #データベース作成のための種類とファイル名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #SQLAlchemyがセッションへの変更を追跡するかどうか
  
db = SQLAlchemy(app) #SQLAlchemyのインスタンスを作成する
#db.init_app(app)


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

#音声認識の連続的な繰り返し
@app.route('/loop_speech_recognition')
def loop_speech_recognition():
	
    return render_template('loop_speech_recognition.html') #html側でこの変数todoを扱えるようにする

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



#アプリとDBの初期化
"""
HatenaBlog, クローラー君アウトプットブログ, 
https://seo-crawler.hatenablog.jp/entry/2023/04/19/095314, 2024年2月14日.
"""
def app_db_init(app, db):
    app.app_context().push()
    db.create_all() #データベースを作成する 初回に1回のみ実行



if __name__ == '__main__':
    #app_db_init(app, db) #データベースを作成する 初回に1回のみ実行
	app.run(debug=True)             #アプリケーションを毎回実行する