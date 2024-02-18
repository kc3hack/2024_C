import requests, tempfile, base64
from playsound import playsound

class Coeiroink:
    domain: str = "http://localhost:50031/"

    def post_audio_query(self, text: str, speaker_id: int = 91):
        uri = self.domain + "audio_query"
        params = {
            "text": text,
            "speaker": speaker_id
        }
        response = requests.post(url=uri, params=params)
        return response.json()

    def post_synthesis_and_play_sound(self, query, speaker_id: int = 91):
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

    def post_synthesis_returned_in_base64(self, query, speaker_id: int = 91):
        uri = self.url + "synthesis"
        params = {
            "speaker": speaker_id
        }
        response = requests.post(
            url=uri,
            params=params,
            json=query
        )
        return base64.b64encode(response.content).decode()