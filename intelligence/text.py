import re
import json
import importlib

from . import plugin

import markdown
import dashscope

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

        to_be_called_tool = assistant_output.tool_calls[0]['function']
        tool_info = {"name": to_be_called_tool['name'], "role": "tool"}
        compound_parameters = json.loads(to_be_called_tool['arguments'])
        to_be_called_function = getattr(plugin, to_be_called_tool['name'])
        tool_info['content'] = to_be_called_function(**compound_parameters)

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
