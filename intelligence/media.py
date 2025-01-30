import json
import os
import re

import markdown
import dashscope

memories = []
with open("./intelligence/prompts/vanilla.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)
    for role, content in prompts.items():
        memories.append({"role": re.sub(r'\d+', '', role), "content": [{"text": content}]})


class PictureUnderstand:
    def __init__(self, api):
        dashscope.api_key = api

    @staticmethod
    def picture_understand(text, image_path, is_search_online):
        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        conversation = {"role": "user",
                        "content": [
                            {"image": f"file://{image_path}"},
                            {"text": text}]}
        memories.append(conversation)
        completion = dashscope.MultiModalConversation().call(
            api_key=dashscope.api_key,
            model="qwen-vl-max",
            messages=memories,
            extra_body=extra_body
        )
        memories.remove(conversation)
        msg = completion["output"]["choices"][0]["message"].content[0]["text"]
        os.remove(image_path)
        return [msg, markdown.markdown(msg)]

