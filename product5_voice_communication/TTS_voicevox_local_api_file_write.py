# PythonからVOICEVOXを実行する

import requests
import json
import sounddevice as sd
import numpy as np

from scipy.io.wavfile import write
# from rich import print
import wave


class TTC_voicevox_local_api_chara:

    def __init__(self, speaker=3):        
        self.host = "127.0.0.1"
        self.port = "50021"
        self.speaker = speaker
        self.frame_sampling = 44100


    def post_audio_query(self, text: str) -> dict:

        # 音声合成用のクエリを作成する
        params = {"text": text, "speaker": self.speaker}
        print("params=" + str(params))

        res = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params,
        )

        print("URL=" + f"http://{self.host}:{self.port}/audio_query")

        query_data = res.json()
        # query_data["speedScale"] = 1.5

        # print("query_data=" + str(query_data))

        return query_data


    def post_synthesis(self, query_data: dict) -> bytes:
        

        # 音声合成を実行する
        params = {"speaker": self.speaker}
        headers = {"content-type": "application/json"}

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            data=json.dumps(query_data),
            params=params,
            headers=headers,
        )

        return res.content


    def write_wavfile(self, wav_data: bytes, path='./music/output.wav'):
        # 音声を再生する
        sample_rate = 24000  # サンプリングレート
        wav_array = np.frombuffer(wav_data, dtype=np.int16)  # バイトデータをnumpy配列に変換
        write(path, sample_rate, wav_array)


    #入力テキスト方式 (テスト用)
    def text_to_voice(self):
        # 入力したテキストをVOICEVOXの音声で再生する
        while True:
            text = input("テキストを入力してください: ")
            if text == "q":
                exit()

            res = self.post_audio_query(text)
            wav = self.post_synthesis(res)
            self.play_wavfile(wav)



    #関数方式 (実装用)
    def TTS_main(self, text, path):
        res = self.post_audio_query(text)
        wav = self.post_synthesis(res)
        self.write_wavfile(wav, path=path)
    




if __name__ == "__main__":

    #TTS_zundamon_class = TTC_voice_vox_local_api_chara(speaker=3)
    #TTS_zundamon_class.text_to_voice()
    """
    メモ

    長音(ー)を付けた方が、音の伸びが良い
    ほとんどの話者は、(ー)と一音
    一部の話者は、(ーー)と二音　つけることで、途中で声が切れるようなことは防げる

    長い文章を話させると反響音のようになってしまう
    https://blog.shikoan.com/voicevox-python/
    で、小さな音声として生成後、正規化などを駆使しながら繋げていくと伸びた良い声になる
    """
    #TTS_zundamon_class.TTS_main("こんにちはー!")
    #TTS_zundamon_class.TTS_main("ずんだもんなのだー!")

    TTS_zundamon_class = TTC_voicevox_local_api_chara(speaker=2)
    #TTS_zundamon_class.TTS_main("こんにちはー!")
    TTS_zundamon_class.TTS_main("こんにちは", path="music/output.wav")
    #TTS_zundamon_class.TTS_main("音声テスト中う")
    #TTS_zundamon_class.TTS_main("音声テスト中なのだー!")
    #TTS_zundamon_class.TTS_main("音声テスト中なのだー。")
        
