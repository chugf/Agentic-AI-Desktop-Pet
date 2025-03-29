import time
import socket
import json

import ollama
import fastapi
from pydantic import BaseModel

deepseek = ollama.Client()
DeepSeekAPI = fastapi.FastAPI()


class Parameters(BaseModel):
    model: str = "deepseek-r1:7b"
    messages: list


@DeepSeekAPI.post("/chat")
def chat(param: Parameters):
    response = deepseek.chat(
        model=param.model,
        messages=param.messages)
    return json.loads(response.model_dump_json())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(DeepSeekAPI, host=socket.gethostbyname(socket.gethostname()), port=int(time.strftime("%Y")))
