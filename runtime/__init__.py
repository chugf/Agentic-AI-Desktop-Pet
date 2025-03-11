import os
import tempfile

import mss
import requests

major = "2"
minor = "1"
patch = "1"


def capture() -> str:
    try:
        os.remove(f"{tempfile.gettempdir()}/screenshot.png")
    except FileNotFoundError:
        pass
    with mss.mss() as sct:
        sct.shot(output=f"{tempfile.gettempdir()}/screenshot.png")
    return f"{tempfile.gettempdir()}/screenshot.png".replace("\\", "/")


def check_update() -> bool:
    latest_version = requests.post("http://adp.nekocode.top/update/version.php")
    if latest_version.text == f"{major}.{minor}.{patch}":
        return False
    else:
        return True
