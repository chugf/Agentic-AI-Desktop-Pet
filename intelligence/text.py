import json
import re
import pathlib
from urllib.parse import unquote, urlparse

import requests
import markdown
import dashscope

memories = []
prompts = {}
tools = [
    # 画画工具 Plating Tool
    {
        "type": "function",
        "function": {
            "name": "draw_picture_by_qwen",
            "description": "当你想要画一副画时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompts": {
                        "type": "string",
                        "description": "画画的提示词，比如：可爱的。"
                    }
                }
            },
            "required": [
                "prompts"
            ]
        }
    }
]


def draw_picture_by_qwen(prompts):
    """画画工具"""
    rsp = dashscope.ImageSynthesis.call(
        model="wanx2.1-t2i-turbo",
        prompt=prompts,
        n=1,
        size='1024*1024')
    filepath = "ERROR"
    for result in rsp.output.results:
        file_name = pathlib.PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        filepath = f"./logs/picture/{file_name}"
        with open(filepath, 'wb+') as f:
            f.write(requests.get(result.url).content)
            f.close()
    return json.dumps({"filepath": filepath})


def clear_memories():
    global memories
    memories = []
    for role, content in prompts.items():
        memories.append({"role": re.sub(r'\d+', '', role), "content": content})


def reload_memories(model):
    global memories, prompts
    try:
        with open(f"./intelligence/prompts/{model}.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
            clear_memories()
    except (FileNotFoundError, FileExistsError):
        memories = []
        prompts = {}


def get_response(extra_body):
    completion = dashscope.Generation().call(
        model="qwen-plus",
        messages=memories,
        presence_penalty=0.6,
        extra_body=extra_body,
        tools=tools
    )
    return completion


class TextGenerator:
    def __init__(self, API_KEY):
        dashscope.api_key = API_KEY

    @staticmethod
    def generate_text(prompt, is_search_online: bool = False):
        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        memories.append({"role": "user", "content": prompt})
        completion = get_response(extra_body)
        assistant_output = completion.output.choices[0].message

        memories.append(assistant_output)
        if 'tool_calls' not in assistant_output:
            return assistant_output.content, markdown.markdown(assistant_output.content)
        elif assistant_output.tool_calls[0]['function']['name'] == 'draw_picture_by_qwen':
            tool_info = {"name": "draw_picture_by_qwen", "role": "tool"}
            prompt = json.loads(assistant_output.tool_calls[0]['function']['arguments'])['prompts']
            tool_info['content'] = draw_picture_by_qwen(prompt)

        memories.append(tool_info)
        final_answer = get_response(extra_body)
        return (final_answer.output.choices[0].message.content,
                markdown.markdown(final_answer.output.choices[0].message.content))


class CustomGenerator:
    def __init__(self, API_KEY, messages: list, is_translate):
        self.messages = messages
        self.is_translate = is_translate
        dashscope.api_key = API_KEY

    def generate_text(self) -> str:
        completion = dashscope.Generation().call(
            model="qwen-mt-turbo",
            messages=self.messages,
            translation_options={
                "source_lang": "Chinese",
                "target_lang": "Japanese"
            }
        )
        message = completion.output.choices[0].message.content
        self.messages.append({"role": "assistant", "content": message})
        return message
