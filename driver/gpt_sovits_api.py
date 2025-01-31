import socket
import json
import threading
import base64
import typing

import os
import glob

import subprocess
import time
import socket

import fastapi
import requests
import uvicorn
from pydantic import BaseModel

MODULE_LIST_PATH = ""

base_url = f"http://{socket.gethostbyname(socket.gethostname())}:{time.strftime("%Y")}"
endpoint_tts = "/tts"                                              # POST
endpoint_change_sovits = "/set_sovits_weights?weights_path={pth}"  # GET
endpoint_change_gpt = "/set_gpt_weights?weights_path={ckpt}"       # GET
CommandReciever = fastapi.FastAPI()
os.system("color 0")


class TTS(BaseModel):
    text: str = ""
    language: typing.Literal['zh', 'en', 'ja', 'ko', 'yue'] = "zh"
    module_name: str = ""
    module_info: dict = {}
    top_k: int = 12
    top_p: float = 0.95,
    temperature: float = 0.34
    speed: float = 1.0
    batch_size: int = 3
    batch_threshold: float = 0.75
    seed: int = -1
    parallel_infer: bool = True
    repetition_penalty: float = 1.35


class Changer(BaseModel):
    module_name: str = ""
    module_info: dict = {}


@CommandReciever.post("/get_module_lists")
def get_module_lists():
    module_dirs_info = [list(zip([MODULE_LIST_PATH + item.split(';')[0]], [item.split(';')[1]])) for item in
                        os.listdir(MODULE_LIST_PATH) if ';' in item]
    module_lists: dict = {}
    for module in module_dirs_info:
        module = module[0]
        module_lists.update({str(module[0].split('\\')[-1]): [  # PTH GPT module
            glob.glob(f"{module[0]};{module[1]}\\*.pth")[0],  # CKPT SOVITS module
            glob.glob(f"{module[0]};{module[1]}\\*.ckpt")[0],  # ref audio
            glob.glob(f"{module[0]};{module[1]}\\*.wav")[0],  # ref prompt text
            f"{module[1]}:" + glob.glob(f"{module[0]};{module[1]}\\*.wav")[0].split('\\')[-1].split('.')[0]]})
    return module_lists


@CommandReciever.post("/change_module")
def change_module(changer: Changer):
    if changer.module_name not in changer.module_info.keys():
        return {"message": "error", "result": f"Failed to set, reason: {changer.module_name} is invalid"}
    requests.get(base_url + endpoint_change_sovits.replace(
        "{pth}",
        changer.module_info[changer.module_name][0]))
    requests.get(base_url + endpoint_change_gpt.replace(
        "{ckpt}",
        changer.module_info[changer.module_name][1]))
    return {"message": "success", "result": True}

@CommandReciever.post("/take_tts")
def tts(param: TTS):
    tts_param = {
        "text": param.text,
        "text_lang": param.language,
        "ref_audio_path": param.module_info[param.module_name][2],
        "prompt_text": param.module_info[param.module_name][3].split(":")[-1],
        "prompt_lang": param.module_info[param.module_name][3].split(":")[0],
        "top_k": param.top_k,
        "top_p": param.top_p,
        "temperature": param.temperature,
        "speed_factor": param.speed,
        "text_split_method": "cut0",
        "batch_size": param.batch_size,
        "batch_threshold": param.batch_threshold,
        "seed": param.seed,
        "parallel_infer": param.parallel_infer,
        "repetition_penalty": param.repetition_penalty
    }
    return json.dumps({
        "message": "success",
        "result": base64.b64encode(requests.post(base_url + endpoint_tts, json=tts_param).content).decode("utf-8")
    })


if __name__ == "__main__":
    threading.Thread(target=subprocess.run, args=(rf".\runtime\python api_v2.py -a "
                                                  rf"{socket.gethostbyname(socket.gethostname())} -p {time.strftime("%Y")}",)).start()
    uvicorn.run(CommandReciever, host=socket.gethostbyname(socket.gethostname()), port=int(time.strftime("%Y")) + 1)
