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

# 需要更改这个
MODULE_LIST_PATH = r""   # ./modules/
"""
MODULE_LIST_PATH: 对GPT-SOVITS模型的文件夹路径进行声明，输入父文件路径
父文件路径下的子文件夹命名规则：
子文件夹为两部分： 1.  模型名字    2.   模型语言
                之间以英文分号“;”分割
子文件夹下的模型： 1.  ckpt和pth模型无特殊要求
                2.  参考音频文件的名字必须为参考音频文本

比如您的文件树：
- gsv
├─────巧克力;ja
│    │      ご主人様のお父様にいつかうまいって言わせてみせるって.wav
│    │      巧克力-e60.ckpt
│    │      巧克力_e10_s3600.pth
│    │
└────├─枫;ja
            ところで、花椒。パンプキンケーキに合わせて茶葉を選んでみたけど。.wav
            枫-e100.ckpt
            枫_e10_s4510.pth

则输入：r"<Your-GSV-Models-Folder>/gsv"

"""

ttk_port = int(time.strftime("%Y")) + 2
command_port = int(time.strftime("%Y")) + 1
ip = socket.gethostbyname(socket.gethostname())
base_url = f"http://{ip}:{ttk_port}"

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


# 定义一个处理获取模块列表请求的函数
# 该函数通过POST方法接收请求，路径为/get_module_lists
@CommandReciever.post("/get_module_lists")
def get_module_lists():
    """
    获取模块列表信息

    该函数扫描MODULE_LIST_PATH路径下的文件，筛选出符合特定格式的模块信息，
    并将其组织成一个字典返回。每个模块的信息包括模块路径下的特定文件类型，
    如.pth、.ckpt和.wav文件，以及从模块路径中提取的相关信息。

    Returns:
        dict: 包含所有模块信息的字典，每个模块的信息包括模型文件路径、检查点文件路径、
              音频文件路径和从音频文件名提取的信息。
    """
    # 构建模块目录信息列表，过滤并组合模块路径和版本号
    module_dirs_info = [list(zip([MODULE_LIST_PATH + item.split(';')[0]], [item.split(';')[1]])) for item in
                        os.listdir(MODULE_LIST_PATH) if ';' in item]
    module_lists: dict = {}
    for module in module_dirs_info:
        module = module[0]
        # 更新模块列表字典，键为模块名，值为包含模块相关文件路径的列表
        module_lists.update({str(module[0].split('\\')[-1]): [
            glob.glob(f"{module[0]};{module[1]}\\*.pth")[0],  # PTH GPT module
            glob.glob(f"{module[0]};{module[1]}\\*.ckpt")[0],  # CKPT SOVITS module
            glob.glob(f"{module[0]};{module[1]}\\*.wav")[0],  # ref audio
            f"{module[1]}:" + glob.glob(f"{module[0]};{module[1]}\\*.wav")[0].split('\\')[-1].split('.')[0]]})  # ref prompt text
    return module_lists


@CommandReciever.post("/change_module")
def change_module(changer: Changer):
    """
    模型切换
    """
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
    response = requests.post(base_url + endpoint_tts, json=tts_param)
    return json.dumps({
        "message": "success",
        "result": base64.b64encode(response.content).decode("utf-8")
    })


if __name__ == "__main__":
    # 一个是启动API，一个是启动命令接收器
    threading.Thread(target=subprocess.run, args=(rf".\runtime\python api_v2.py -a "
                                                  rf"{ip} -p {ttk_port}",)).start()
    uvicorn.run(CommandReciever, host=ip, port=command_port)
