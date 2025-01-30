from urllib.parse import urlencode
import datetime
import hashlib
import json
from datetime import datetime
from time import mktime
import base64

import _thread as thread

import hmac
import ssl
from wsgiref.handlers import format_date_time
import websocket
import pyaudio

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

API_ID = ""
API_KEY = ""
API_SECRET = ""


class RealTimeSpeechRecognizer:
    def __init__(self, success_func, error_func, close_func):
        self.is_status = False
        self.is_continue = True
        self.success_func = success_func
        self.error_func = error_func
        self.close_func = close_func

        self.CommonArgs = {"app_id": API_ID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    @staticmethod
    def create_url():
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            API_KEY, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

    def closed(self):
        self.is_continue = False

    def statued(self):
        self.is_status = True

    def on_message(self, ws, message):
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                self.error_func(sid, errMsg)
            else:
                data = json.loads(message)["data"]["result"]["ws"]
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                self.success_func(json.loads(json.dumps(data, ensure_ascii=False)))
        except Exception as e:
            self.error_func(e, None)

    def on_error(self, ws, error):
        self.error_func(error, None)

    def on_close(self, ws, a, b):
        self.is_continue = False
        self.close_func()

    def on_open(self, ws):
        def run(*args):
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = int(RATE * 0.04)

            audio = pyaudio.PyAudio()

            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)

            status = STATUS_FIRST_FRAME

            while self.is_continue:
                buf = stream.read(CHUNK)
                if not buf:
                    continue
                if self.is_status:
                    status = STATUS_LAST_FRAME
                    self.is_status = False
                if status == STATUS_FIRST_FRAME:
                    d = {"common": self.CommonArgs,
                         "business": self.BusinessArgs,
                         "data": {"status": 0, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": f"audio/L16;rate={RATE}",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    break

            stream.stop_stream()
            stream.close()
            audio.terminate()
            ws.close()

        thread.start_new_thread(run, ())

    def start_recognition(self):
        websocket.enableTrace(False)
        wsUrl = self.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    def s(data):
        print(data)


    def e(error, code):
        print(error, code)


    def c():
        print("close")


    recognizer = RealTimeSpeechRecognizer(s, e, c)
    recognizer.start_recognition()
