# coeiroink.py

import requests, tempfile, base64
from playsound import playsound

class Coeiroink:
    domain: str = "http://localhost:50021/"

    def post_audio_query(self, text: str, speaker_id: int = 2):
        uri = self.domain + "audio_query"
        params = {
            "text": text,
            "speaker": speaker_id
        }
        response = requests.post(url=uri, params=params)
        return response.json()

    def post_synthesis_and_play_sound(self, query, speaker_id: int = 2):
        uri = self.domain + "synthesis"
        params = {
            "speaker": speaker_id
        }
        response = requests.post(
            url=uri,
            params=params,
            json=query
        )
        print(response.status_code)
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(response.content)
            fp.seek(0)
            playsound(fp.name)
        return response.content


coeiroink = Coeiroink()
query = coeiroink.post_audio_query("テスト")
coeiroink.post_synthesis_and_play_sound(query)