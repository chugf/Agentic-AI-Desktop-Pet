import json

from . import constants


def change_configure(value, relative, configure):
    temp_dict = configure

    for key in relative.split(".")[:-1]:
        if key not in temp_dict:
            temp_dict[key] = {}
        temp_dict = temp_dict[key]

    if relative.split("."):
        last_key = relative.split(".")[-1]
        temp_dict[last_key] = value

    with open(constants.CONFIGURE_PATH, "w", encoding="utf-8") as cf:
        json.dump(configure, cf, ensure_ascii=False, indent=3)
        cf.close()
