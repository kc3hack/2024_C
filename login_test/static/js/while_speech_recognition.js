//自動音声認識
/*
Qiita, たった17行のコードで音声自動文字起こしを実装する, 
https://qiita.com/kolife/items/a0af7702eef05994fbfb
*/

const speech = new webkitSpeechRecognition();
speech.lang = 'ja-JP';

const btn = document.getElementById('btn');
const content = document.getElementById('content');

btn.addEventListener('click' , function() {
    speech.start();
});

speech.onresult = function(e) {
        speech.stop();
        if(e.results[0].isFinal){
            var autotext =  e.results[0][0].transcript
            content.innerHTML += '<div>'+ autotext +'</div>';
        }
    }

    speech.onend = () => { 
    speech.start() 
    };