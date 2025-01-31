import json
import re

import markdown
import dashscope

memories = []
prompts = {}


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


class TextGenerator:
    def __init__(self, API_KEY):
        dashscope.api_key = API_KEY

    def generate_text(self, prompt, is_search_online: bool = False):
        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        memories.append({"role": "user", "content": prompt})
        completion = dashscope.Generation().call(
            model="qwen-plus",
            messages=memories,
            extra_body=extra_body,
            presence_penalty=0.6,
        )
        message = completion.output.text
        memories.append({"role": "assistant", "content": message})
        return message, markdown.markdown(message)


class CustomGenerator:
    def __init__(self, API_KEY, messages: list, is_translate):
        self.messages = messages
        self.is_translate = is_translate
        dashscope.api_key = API_KEY

    def generate_text(self):
        translation_option = {}
        if self.is_translate:
            translation_option = {
                "source_lang": "Chinese",
                "target_lang": "Japanese"
            }
        completion = dashscope.Generation().call(
            model="qwen-mt-turbo",
            messages=self.messages,
            translation_options=translation_option
        )
        message = completion.output.choices[0].message.content
        self.messages.append({"role": "assistant", "content": message})
        return message
