// 変数
var audioContext //音響処理の実体を格納
var mediaStreamSource
var meter

var time_count = 0 //時間を数える

//音声認識の初期化
//SpeechRecognition = webkitSpeechRecognition || SpeechRecognition;
//const recognition = new SpeechRecognition();

//音声認識のアラートをする関数
/*
recognition.onresult = (event) => {
  alert(event.results[0][0].transcript);
  //document.getElementById('edit_area').textContent = event.results[0][0].transcript;
}
*/


// ボリューム検出の開始
function beginDetect() {
  // オーディオストリームの生成
  audioContext = new (window.AudioContext || window.webkitAudioContext)()
 
  // 音声入力の開始
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({audio: true}).then((stream) => {
      // メディアストリームソースとメーターの生成
      mediaStreamSource = audioContext.createMediaStreamSource(stream)
      meter = createAudioMeter(audioContext)
      mediaStreamSource.connect(meter)
    })
  }
}

// メーターの生成
function createAudioMeter(audioContext, clipLevel, averaging, clipLag) {
  // メーターの生成
  const processor = audioContext.createScriptProcessor(512)
  processor.onaudioprocess = volumeAudioProcess
  processor.clipping = false
  processor.lastClip = 0
  processor.volume = 0
  processor.clipLevel = clipLevel || 0.98
  processor.averaging = averaging || 0.95
  processor.clipLag = clipLag || 750
  processor.connect(audioContext.destination)

  // クリップチェック時に呼ばれる
  processor.checkClipping = function() {
    if (!this.clipping) {
      return false
    }
    if ((this.lastClip + this.clipLag) < window.performance.now()) {
      this.clipping = false
    }
    return this.clipping
  }

  // シャットダウン時に呼ばれる
  processor.shutdown = function() {
    this.disconnect()
    this.onaudioprocess = null
  }

  return processor
}

// オーディオ処理時に呼ばれる
function volumeAudioProcess(event) {
  const buf = event.inputBuffer.getChannelData(0)
  const bufLength = buf.length
  let sum = 0
  let x
  const volume_TH = 0.05 //音声認識開始閾値
  let recognition_state = '停止'

  // 平均ボリュームの計算
  for (var i = 0; i < bufLength; i++) {
    x = buf[i]
    if (Math.abs(x) >= this.clipLevel) {
        this.clipping = true
        this.lastClip = window.performance.now()
    }
    sum += x * x
  }
  const rms = Math.sqrt(sum / bufLength)
  this.volume = Math.max(rms, this.volume * this.averaging)

  //ボリュームが閾値を超えたときに音声認識開始
  if (this.volume > volume_TH) {
    recognition_state = '中'
    time_count = 1
    //alert("音声認識");
    //recognition.start(); //音声認識開始
  }

  if (time_count > 0 && time_count < 500){
    time_count += 1 
    recognition_state = '中'
  }
  else{
    time_count = 0
    recognition_state = '停止'
  }

  

  /*
  else {
    recognition_state = '停止'
  }
  */

 
  // ボリュームの表示
  output.innerHTML = 'ボリューム: ' + this.volume.toFixed(4) //toFixed(小数点以下切り捨て)
  output2.innerHTML = '音声認識: ' + recognition_state + time_count
}