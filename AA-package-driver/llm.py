import time
import os
import socket
import json

import ollama
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


allowed_api = "heavynotfat"
deepseek = ollama.Client()
DeepSeekAPI = fastapi.FastAPI()


class Parameters(BaseModel):
    api: str
    model: str
    messages: list


@DeepSeekAPI.post("/chat")
def chat(param: Parameters):
    def event_generator():
        if param.api != allowed_api:
            yield json.dumps({'message': {'content': 'Invalid API key'}})
        else:
            response = deepseek.chat(
                stream=True,
                model=param.model,
                messages=param.messages)
            for chunk in response:
                yield json.dumps({'message': {'content': chunk.message.content}})
    return StreamingResponse(event_generator(), media_type="text/event-stream")


os.system("color 0")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(DeepSeekAPI, host=socket.gethostbyname(socket.gethostname()), port=int(time.strftime("%Y")))
