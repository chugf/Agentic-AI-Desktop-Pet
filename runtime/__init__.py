import os
import tempfile

import mss


def capture() -> str:
    try:
        os.remove(f"{tempfile.gettempdir()}/screenshot.png")
    except FileNotFoundError:
        pass
    with mss.mss() as sct:
        sct.shot(output=f"{tempfile.gettempdir()}/screenshot.png")
    return f"{tempfile.gettempdir()}/screenshot.png".replace("\\", "/")


def record_system():
    ...
