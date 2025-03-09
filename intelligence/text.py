import re
import json
import importlib

from . import external

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
    importlib.reload(external)
    with open("./resources/functions.json", "r", encoding="utf-8") as ff:
        tools = json.load(ff)
        tool_names = []
        properties = {}
        for tool in tools:
            tool_names.append(tool['function']['name'])
            properties.update({tool['function']['name']: list(tool['function']['parameters']['properties'].keys())})
        ff.close()


def TextGeneratorLocal(prompt, func, url):
    memories.append({"role": "user", "content": prompt})
    response = requests.post(url, json={"model": "deepseek-r1:8b", "messages": memories})
    answer = response.json()
    memories.append({'role': 'assistant', 'content': answer['message']['content']})
    func(answer['message']['content'],
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
                stream=True,
                tools=tools
            )
        else:
            completion = dashscope.Generation().call(
                model=model,
                messages=memories,
                presence_penalty=0.6,
                stream=True,
                extra_body=extra_body
            )
        return completion

    def generate_text(self, prompt, model, func: callable,
                      is_search_online: bool = False):
        def process_chunks(completion_, memories_, extra_body_, model_, external_):
            chunk_message = None
            for chunk in completion_:
                if chunk.status_code == 400:
                    return False
                chunk_message = chunk.output.choices[0].message

                if 'tool_calls' in chunk_message:
                    if chunk.output.choices[0].finish_reason == 'tool_calls':
                        memories_.append(chunk_message)
                        to_be_called_tool = chunk_message.tool_calls[0]['function']
                        tool_info = {"name": to_be_called_tool['name'], "role": "tool"}

                        compound_parameters = json.loads(to_be_called_tool['arguments'])
                        to_be_called_function = getattr(external_, to_be_called_tool['name'])
                        tool_info['content'] = to_be_called_function(**compound_parameters)
                        memories_.append(tool_info)

                        new_completion = self.get_response(extra_body_, model_)
                        return process_chunks(new_completion, memories_, extra_body_, model_, external_)
                else:
                    memories_.append(chunk_message)
                    if 'reasoning_content' in chunk_message.keys() and \
                            not chunk_message.content.strip() and chunk_message['reasoning_content'].strip():
                        func((None, markdown.markdown(f"<think>\n{chunk_message['reasoning_content']}\n</think>")))
                    else:
                        func((chunk_message.content, markdown.markdown(chunk_message.content)))
            return chunk_message

        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        memories.append({"role": "user", "content": prompt})

        completion = self.get_response(extra_body, model)
        check_answer = process_chunks(completion, memories, extra_body, model, external)
        if check_answer is not False:
            return check_answer.content
        else:
            completion = self.get_response(extra_body, model, False)
            return process_chunks(completion, memories, extra_body, model, external).content


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
