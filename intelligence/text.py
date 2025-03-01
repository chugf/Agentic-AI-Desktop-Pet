import re
import json
import importlib

from . import plugin

import markdown
import dashscope
import requests

memories = []
prompts = {}
with open("./resources/functions.json", "r", encoding="utf-8") as ff:
    tools = json.load(ff)
    tool_names = []
    properties = {}
    for tool in tools:
        tool_names.append(tool['function']['name'])
        properties.update({tool['function']['name']: list(tool['function']['parameters']['properties'].keys())})
    ff.close()


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


def reload_tools():
    global tools, tool_names, properties
    importlib.reload(plugin)
    with open("./resources/functions.json", "r", encoding="utf-8") as ff:
        tools = json.load(ff)
        tool_names = []
        properties = {}
        for tool in tools:
            tool_names.append(tool['function']['name'])
            properties.update({tool['function']['name']: list(tool['function']['parameters']['properties'].keys())})
        ff.close()


def TextGeneratorLocal(prompt, url) -> tuple:
    memories.append({"role": "user", "content": prompt})
    response = requests.post(url, json={"model": "deepseek-r1:8b", "messages": memories})
    answer = response.json()
    memories.append({'role': 'assistant', 'content': answer['message']['content']})
    return (answer['message']['content'],
            markdown.markdown(answer['message']['content']))


class TextGenerator:
    def __init__(self, API_KEY):
        dashscope.api_key = API_KEY

    @staticmethod
    def get_response(extra_body, model, enable_tools: bool = True):
        if enable_tools:
            completion = dashscope.Generation().call(
                model=model,
                messages=memories,
                presence_penalty=0.6,
                extra_body=extra_body,
                tools=tools
            )
        else:
            completion = dashscope.Generation().call(
                model=model,
                messages=memories,
                presence_penalty=0.6,
                extra_body=extra_body
            )
        return completion

    def generate_text(self, prompt, model,
                      is_search_online: bool = False):
        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        memories.append({"role": "user", "content": prompt})
        completion = self.get_response(extra_body, model)
        if completion.status_code == 400:
            completion = self.get_response(extra_body, model, False)

        assistant_output = completion.output.choices[0].message

        memories.append(assistant_output)
        while 'tool_calls' in assistant_output:
            to_be_called_tool = assistant_output.tool_calls[0]['function']
            tool_info = {"name": to_be_called_tool['name'], "role": "tool"}
            compound_parameters = json.loads(to_be_called_tool['arguments'])
            to_be_called_function = getattr(plugin, to_be_called_tool['name'])
            tool_info['content'] = to_be_called_function(**compound_parameters)

            memories.append(tool_info)
            multiple_answer = self.get_response(extra_body, model)
            assistant_output = multiple_answer.output.choices[0].message
            memories.append(assistant_output)

        return (assistant_output.content,
                markdown.markdown(assistant_output.content))


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
