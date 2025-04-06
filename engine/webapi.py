import json
from socket import gethostname, gethostbyname
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from uvicorn import run as serve

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{gethostbyname(gethostname())}:52013"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

intelligence = None
model = None
api_config = None
languages = None
url = None


def reload_module(intelligence_module):
    global intelligence
    intelligence = intelligence_module


def reload_data(new_model, new_api_config, new_languages, new_url):
    global model, api_config, languages, url
    model = new_model
    api_config = new_api_config
    languages = new_languages
    url = new_url


@app.post("/chat")
async def chat(request: Request):
    upload_data = await request.json()
    question = upload_data.get('question')

    def generate():
        for chunk in intelligence.text_generator(question, model, False, api_config, languages, url):
            yield json.dumps({'message': {'content': chunk}}) + "\n"

    return StreamingResponse(generate(), media_type='application/json')


@app.post("/upload-image")
async def upload_image(request: Request):
    upload_data = await request.json()
    upload_url = upload_data.get('url')

    if os.path.exists(upload_url):
        os.rename(upload_url,
                  f'{os.getcwd()}/engine/static/images/{os.path.basename(upload_url)}')
    new_url = f"./static/images/{os.path.basename(upload_url)}"
    return Response(json.dumps({"url": new_url}))


def run():
    serve(app, host=gethostbyname(gethostname()), port=12877)


if __name__ == "__main__":
    run()
