//音声認識
//Qiita, Webページでブラウザの音声認識機能を使おう - Web Speech API Speech Recognition
//https://qiita.com/hmmrjn/items/4b77a86030ed0071f548


SpeechRecognition = webkitSpeechRecognition || SpeechRecognition;
const recognition = new SpeechRecognition();

recognition.onresult = (event) => {
alert(event.results[0][0].transcript);
}

recognition.start();
