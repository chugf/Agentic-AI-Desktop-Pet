import time
import os
import socket
import json

import ollama
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# API密钥
allowed_api = "heavynotfat"
client = ollama.Client()
CustomAPI = fastapi.FastAPI()


class Parameters(BaseModel):
    """API参数设定，更改需要对应更改程序的文本输出API部分"""
    # API对比allowed_api的值
    # API在人工智能 -> 本地推理 -> 文本输出API的API-Key字段的value（第二框）填写allowed_api的值
    api: str          # 在 人工智能 -> 本地推理 -> 文本输出API 的API-Key字段的Endpoint（第一框）
    model: str        # 在 人工智能 -> 本地推理 -> 文本输出API 的Model字段的Endpoint（第一框）
    messages: list    # 在 人工智能 -> 本地推理 -> 文本输出API 的Messages字段的Endpoint


@CustomAPI.post("/chat")
def chat(param: Parameters):
    """
    提供聊天功能的API接口。
    """
    def event_generator():
        # 对比API密钥
        if param.api != allowed_api:
            yield json.dumps({'message': {'content': 'Invalid API key'}})
        else:
            response = client.chat(
                stream=True,
                model=param.model,
                messages=param.messages)
            for chunk in response:
                yield json.dumps({'message': {'content': chunk.message.content}})
    return StreamingResponse(event_generator(), media_type="text/event-stream")


os.system("color 0")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(CustomAPI, host=socket.gethostbyname(socket.gethostname()), port=int(time.strftime("%Y")))
