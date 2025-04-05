import json
from socket import gethostname, gethostbyname

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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


def run():
    serve(app, host=gethostbyname(gethostname()), port=12877)


if __name__ == "__main__":
    run()
