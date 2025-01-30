from typing import Literal

import socket
import json
import time

import io
import wave
import pyaudio

import requests

import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts import ResultCallback, SpeechSynthesizer, SpeechSynthesisResult


wlan_ip = socket.gethostbyname(socket.gethostname())
# API endpoint
base_url = f"http://{wlan_ip}:{time.strftime("%Y")}"
endpoint_tts = "/tts"  # POST
endpoint_change_sovits = "/set_sovits_weights?weights_path={pth}"  # GET
endpoint_change_gpt = "/set_gpt_weights?weights_path={ckpt}"       # GET


# TCP Client
class Client:
    def __init__(self, ip=wlan_ip, port=int(time.strftime("%Y")) + 1):
        self.host = ip
        self.port = port
        self.client_socket = None

    def command(self, command: dict):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Connected {(self.host, self.port)}")

        send_data = json.dumps(command)
        self.client_socket.sendall(send_data.encode('utf-8'))

        response = b''
        while True:
            data = self.client_socket.recv(65535)
            if data:
                response += data
            else:
                break

        self.client_socket.close()

        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)

        return response_dict


def play_audio_by_bytes(wav_bytes: bytes):
    p = pyaudio.PyAudio()
    with io.BytesIO(wav_bytes) as wav_file:
        with wave.open(wav_file, 'rb') as wf:
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
    p.terminate()


def change_module(name: str, module_info: dict):
    if name not in module_info.keys():
        return (f"Failed to set, reason: {name} is invalid\n"
                f"{list(module_info.keys())}")
    requests.get(base_url + endpoint_change_sovits.replace(
        "{pth}",
        module_info[name][0]))
    requests.get(base_url + endpoint_change_gpt.replace(
        "{ckpt}",
        module_info[name][1]))
    return True


def take_a_tts(text: str, language: Literal['zh', 'en', 'ja', 'ko', 'yue'], module_info: dict, module_name: str,
               top_k: int = 12, top_p: float = 0.95, temperature: float = 0.34, speed: float = 1.0,
               batch_size: int = 3, batch_threshold: float = 0.75,
               seed: int = -1, parallel_infer: bool = True, repetition_penalty: float = 1.35):
    tts_param = {
        "text": text,
        "text_lang": language,
        "ref_audio_path": module_info[module_name][2],
        "prompt_text": module_info[module_name][3].split(":")[-1],
        "prompt_lang": module_info[module_name][3].split(":")[0],
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "speed_factor": speed,
        "text_split_method": "cut0",
        "batch_size": batch_size,
        "batch_threshold": batch_threshold,
        "seed": seed,
        "parallel_infer": parallel_infer,
        "repetition_penalty": repetition_penalty
    }
    response = requests.post(base_url + endpoint_tts, json=tts_param)
    return response.content


def ali_tts(text: str, api):
    dashscope.api_key = api
    result_voice: SpeechSynthesisResult | None = None

    class Callback(ResultCallback):
        def on_open(self):
            pass

        def on_complete(self):
            pass

        def on_error(self, response: SpeechSynthesisResponse):
            pass

        def on_close(self):
            pass

        def on_event(self, result: SpeechSynthesisResult):
            nonlocal result_voice
            result_voice = result

    callback = Callback()
    result = SpeechSynthesizer.call(model='sambert-zhiqi-v1',
                                    text=text,
                                    sample_rate=48000,
                                    format='wav',
                                    callback=callback,
                                    word_timestamp_enabled=True,
                                    )

    if result.get_audio_data() is not None:
        return result.get_audio_data(), int(result_voice.get_timestamp()['end_time'])
    return None


if __name__ == "__main__":
    MODULE_INFO = Client().command({"module_info": None})
    print(list(MODULE_INFO.keys()))
    while True:
        module = str(input())
        if module in MODULE_INFO.keys():
            change_module(module, MODULE_INFO)
            play_audio_by_bytes(take_a_tts(input("Content > "), "zh", MODULE_INFO, module))
        else:
            print(f"没有{module}模型\n", list(MODULE_INFO.keys()))

