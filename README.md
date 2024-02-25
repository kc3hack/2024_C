# 関西えぇgent 
<!-- プロダクト名に変更してください -->

[kansaieegent](skansai_eegent_logo.png)

<!--[関西えぇgent](https://github.com/kc3hack/2024_C/blob/backend/kansai_eegent_logo.png?raw=true)-->

<!--![プロダクト名](https://kc3.me/cms/wp-content/uploads/2023/11/2b1b6d9083182c0ce0aeb60000b4d7a7.png)-->
<!-- プロダクト名・イメージ画像を差し変えてください -->


## チーム名
チームC 関西開拓者
<!-- チームIDとチーム名を入力してください -->


## 背景・課題・解決されること

<!-- テーマ「関西をいい感じに」に対して、考案するプロダクトがどういった(Why)背景から思いついたのか、どのよう(What)な課題があり、どのよう(How)に解決するのかを入力してください -->
### 背景
* 関東は東京に都心が集中した一極集中型なのに対して、関西は京都/大阪/神戸に分散した多極型の都市構造になっており、各県が広く繁栄している。
* 単純な都市規模の違いだけでなく、並行路線の数が多くJRと私鉄が各方面で競合しているため各拠点駅が分散状態である。
* また関西にはただの近代的なビルを建設するだけでなく、各都市ごとに異なる文化と歴史がある。

### 課題
* 観光シーズンになると古都の街並みや、有名なお寺をじっくりと眺めるどころではないくらい観光客が増加している。

### 解決　
* 観光客の分散を促せるために各県・各地域の隠れスポットを紹介するagentを開発した。
関西の繁栄　https://www.sikenteki.com/entry/2020/12/21/011153
大阪訪問　　https://lifepepper.co.jp/inbound/why-popular-osaka/
オーバーツーリズム　　https://www.ktv.jp/news/feature/231006-overtourism/


## プロダクト説明

<!-- 開発したプロダクトの説明を入力してください -->
* 有名な観光地を訪問した際の現在地を得ることでその付近の「隠れたええところ」をGPS情報で取得する。近い10個のスポットの中からユーザが好きなスポットを1つ選び、そのスポットの名前、住所、や概要を知る。さらにそれだけでは知りえなかったことを口コミやユーザーによる直接の説明を参照することでAIのAgentとおしゃべりしながら知ることができる。


## 操作説明・デモ動画
[デモ動画はこちら](https://www.youtube.com/watch?v=_FAA15ARmas)
<!-- 開発したプロダクトの操作説明について入力してください。また、操作説明デモ動画があれば、埋め込みやリンクを記載してください -->

### 1頁目:SignInとSignUpの画面

* ユーザーが決めたユーザーID、メールアドレスやパスワードを入力してサインアップ。サインアップします。
(ユーザーIDはローマ字で記述してください)



### 2頁目:隠れスポット入力画面

* 後に隠れスポットの登録画面に移行し、画面で隠れスポットの名前と住所、概要や詳細情報を入力する。これでユーザー登録が完了し、以後ユーザーIDとパスワードでログインが可能となる。
(サインアップ時のみ隠れスポットの入力が必須となります)



### 3頁目:音声対話の画面


「画面構成」
* 画面上部に現在地付近のスポットの名前と住所が10個表示されます。
* サイトを開いたときから音声を受け付けています。
* 話しかけても聴いてくれない場合は音声認識開始ボタンを押してください


「操作手順」
対話は4段階構成です。

(1段階目 10個のスポットから1つを番号で選択)
1. 例えば, 4番目のスポットが良いと感じた場合は「4番」や「4」など声で発話して入力します　
2. 次に音声合成ボタンを押すと文章をAgentが読み上げてくれます。
(Agentの文章が変わらない場合はもう一度押してください)

(2段階目 スポットの確認)
1. 音声合成ボタンをクリックすると例えば「4番目で良いか」を確かめる内容を発話します。
(もし、間違えている場合は最初のページに戻って、選び直してください)

(3段階目 スポットの概要)
1. 音声合成ボタンをクリックすると 例えば「4番目の概要」を
を話します。

(4段階目 スポットについての質問応答)
1. スポットについての質問を音声で話してください。
2. 質問の回答が得られるまで音声合成ボタンを押してください。
3. すると短い文でAgentが方言を使い回答してくれます。
「地図頁へ行くボタン」を押すと地図による視覚的な位置を確認することができます。



### 4頁目:地図対話の画面

「画面構成」
* 上部に現在地付近の地図が表示されています。
現在地とスポットのところにピンが立っています。
ピンをクリックすると何番目のスポットかが表示されます。
* 下部に音声対話の画面と同様にスポットの名前と住所が記載されています。

「操作方法」
* 地図を指で動かすと見たい場所でスクロールできます。
* 「音声頁へ行くボタン」を押すと続きから音声対話をすることができます。


## 注力したポイント

<!-- 開発したプロダクトの中で、特に注力して作成した箇所・ポイントについて入力してください -->

### 黎明期の知識
* 黎明期のユーザーでも隠れスポットを知ることができるように、 ([1] じゃらん様)の概要を引用させて頂き, 口コミの内容を参照しスポットの情報をAIのAgentが自分の言葉で説明しなおした内容を提供しております。
(※ じゃらん様のサーバへ負荷が及ばないように概要や口コミ等のデータは私たちのチームのPCに保存させて頂きました。 参照される際にはサーバである私たちのPCのみに負荷が及ぶようにしております。また、これらの情報は全てじゃらん様のサイトで閲覧可能です。)

### 聴覚と発話
* 音声認識と([2]VOICEVOX:春日部つむぎ)による音声合成を活用することで, 文字を打つことなく、 声とボタンのクリックでやりとりすることができます。手間が削減されるため旅行や外出の途中に使いやすいです。

### 会話の記憶
* ユーザーとの会話履歴をプロンプトに入れる仕組みにより, 同じセッション内では過去の会話履歴を参照して対話することができます。

### 会話の再開
* 音声でのやり取りによる聴覚的なページと地図での位置表示の視覚的なページを用意しました。それらのページを閲覧することで、2つの側面から隠れスポットを確認することができます。

### 外部知識の参照
* Retrieval Augmented Generation（RAG）を用いました. これにより, ]ユーザーや口コミに含まれる範囲でその文を参照して回答することができるため, ChatGPTで一般的に心配される本当のような嘘をつく問題が大幅に解消されます。

### 言葉遣い
* 京都弁, 神戸弁や大阪弁といった地域ごとに話方を変えることで地域の風情も楽しむことができます。
(※ 京都府:京都弁, 兵庫県:神戸弁: その他の地域:大阪弁) 

### デザインと見やすさ
* 背景の画像がスライドショーになるように設定し、見やすいように枠で囲うなど工夫した。
* マップでカーソルを合わせると名前が出るようにし、クリックすると画像が出るようにした。
* 説明や概要を登録する際に、長くなりすぎて他のユーザーが閲覧しやすくすることを前提に概要と説明に文字数制限を設けた。


[1] じゃらん PRODUCED BY RECRUIT, https://www.jalan.net/dayuse/?ccnt=global_navi
[2] VOICEVOX, https://voicevox.hiroshiba.jp/

## 使用技術

<!-- 使用技術を入力してください -->
### バックエンド

```
ノートPC Windows  
.
└── python
    ├── サーバやhttpとsocket通信
    │   ├── flask        :webアプリケーションの作成
    │   ├── sqlalchemy   :データベースの操作
    │   ├── requests　   :httpリクエストの取得
    │   ├── BeautifulSoup:じゃらん様サイトのhtmlデータの抽出
    │   ├── json         :json形式データの操作
    │   └── urllib       :日本語URLの符号化
    ├── 言語処理
    │   ├── llama_index  :RAGによる大規模言語モデルの外部知識参照
    │   ├── langchain   :大規模言語モデルの会話の記憶
    │   ├── Levenshtein :レーベンシュタイン距離による文字列類似度
    │   └── re          :正規表現
    ├── ファイル入出力
    │   ├── numpy       :音声ファイル読込み
    │   ├── scipy       :音声ファイル書き出し
    │   ├── csv         :じゃらん様から取得させて頂いたデータの保管
    │   └── os          :ファイル操作
    └── その他
        ├── geopy　　　  :緯度経度での距離計算
        └── time        :プログラム内での一時停止
.
└── ソフトウェア
    └── VOICEVOX:春日部つむぎ :音声合成 
.
└── API
    ├── OpenAIのgpt3.5-turbo :大規模言語モデル
    └── https://msearch.gsi.go.jp/address-search/AddressSearch :国土交通省 住所のGPSへの変換
```


### フロントエンド
```
ノートPCやスマートフォンのブラウザ  
.   
├── html
├── css
│   └── https://unpkg.com/leaflet/dist/leaflet.css : leafletの現在地と地図
└── javascript
    ├── https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.js : ajax通信
    └── https://unpkg.com/leaflet/dist/leaflet.js : leafletの現在地と地図 
.
└── API
    ├── webkitSpeechRecognition : 音声認識
    └── https://tile.openstreetmap.org : 表示する地図の画像 
```
  
<!--
markdownの記法はこちらを参照してください！
https://docs.github.com/ja/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
-->
