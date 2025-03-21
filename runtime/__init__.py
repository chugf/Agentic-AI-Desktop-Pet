import os
import tempfile
import ast
import threading
import ctypes
import time
import re

import mss
import requests
import win32api
import win32con

major = "3"
minor = "0"
patch = "0"


class ThreadExceptionEnd(threading.Thread):
    """结束线程 End Thread"""
    def __init__(self, func: callable, finished=None):
        threading.Thread.__init__(self)
        self.func = func
        self.finished = finished

    def run(self):
        self.func()
        if self.finished is not None:
            self.finished()

    def stop_thread(self):
        thread_id = self._get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            return False
        return True

    def _get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id_, thread_ in threading._active.items():
            if thread_ is self:
                return id_


class ExtractFunctionDocstring(ast.NodeVisitor):
    """提取函数文档字符串 Extract function docstring"""
    def __init__(self, function_name):
        self.function_name = function_name
        self.description = None

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.Module) and node.name == self.function_name:
            docstring = ast.get_docstring(node)
            if docstring:
                lines = docstring.split('\n')
                if lines:
                    self.description = lines[0].strip()
        return node

    @staticmethod
    def add_parents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    def extract(self, code):
        tree = ast.parse(code)
        self.add_parents(tree)
        visitor = ExtractFunctionDocstring(self.function_name)
        visitor.visit(tree)

        return visitor.description


class RemoveFunctionTransformer(ast.NodeTransformer):
    """移除函数 Remove function"""
    def __init__(self, function_name):
        self.function_name = function_name

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.Module) and node.name == self.function_name:
            return None
        return node

    @staticmethod
    def add_parents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    def remove(self, code):
        tree = ast.parse(code)
        self.add_parents(tree)
        transformer = RemoveFunctionTransformer(self.function_name)
        new_tree = transformer.visit(tree)

        return ast.unparse(new_tree)


# 鼠标监听器 Mouse listener
class MouseListener:
    """用于在全局鼠标穿透下进行监听 Used for global mouse penetration to listen"""
    def __init__(self):
        self.listener_thread = None
        self.isListening = False
        self.is_left_button_pressed = False
        self.is_right_button_pressed = False

    def start_listening(self):
        self.isListening = True
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def stop_listening(self):
        self.__init__()

    def listen(self):
        state_left = 0
        state_right = 0
        while self.isListening:
            current_state_left = win32api.GetKeyState(win32con.VK_LBUTTON)
            current_state_right = win32api.GetKeyState(win32con.VK_RBUTTON)
            if current_state_left != state_left:
                state_left = current_state_left
                if current_state_left < 0:
                    self.is_left_button_pressed = True
                else:
                    self.is_left_button_pressed = False
            if current_state_right != state_right:
                state_right = current_state_right
                if current_state_right < 0:
                    self.is_right_button_pressed = True
                else:
                    self.is_right_button_pressed = False
            threading.Event().wait(0.01)


class PythonCodeParser(ast.NodeVisitor):
    """Parse plugin code"""
    def __init__(self, code):
        super().__init__()
        self.called = [False] * 10
        self.analyze_code(code)

    @property
    def has_subscribe(self):
        return self.called[0]

    @property
    def has_subscribe_for_views(self):
        return self.called[1]

    @property
    def has_subscribe_for_actions(self):
        return self.called[2]

    def analyze_code(self, code):
        tree = ast.parse(code)
        self.visit(tree)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            current_node = node.func
            parts = []
            while isinstance(current_node, ast.Attribute):
                parts.append(current_node.attr)
                current_node = current_node.value
            if isinstance(current_node, ast.Name):
                parts.append(current_node.id)
                full_call_path = '.'.join(reversed(parts)).split(".")
                if full_call_path[0] == "subscribe":
                    self.called[0] = True
                if full_call_path[0] == "subscribe" and full_call_path[1] == "views":
                    self.called[1] = True
                if full_call_path[0] == "subscribe" and full_call_path[1] == "actions":
                    self.called[2] = True
        self.generic_visit(node)


def parse_local_url(url: str):
    truly_url = url.format(
        ip=__import__("socket").gethostbyname(__import__("socket").gethostname()),
        year=time.strftime("%Y"),
    )
    cleaned_url = re.sub(r'\s*\+\s*', '+', truly_url)
    pattern = r'^(http|https)://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:(.*?))?(/.*)?$'
    match = re.match(pattern, cleaned_url)
    if match:
        request_header = match.group(1)
        ip = match.group(2)
        port_part = match.group(4) if match.group(4) else '80'
        path = match.group(5) if match.group(5) else '/'
        try:
            port = str(eval(port_part)) if port_part else '80'
        except Exception:
            return url

        return f"{request_header}://{ip}:{port}{path}"
    return url


def capture() -> str:
    try:
        os.remove(f"{tempfile.gettempdir()}/screenshot.png")
    except FileNotFoundError:
        pass
    with mss.mss() as sct:
        sct.shot(output=f"{tempfile.gettempdir()}/screenshot.png")
    return f"{tempfile.gettempdir()}/screenshot.png".replace("\\", "/")


def check_update():
    try:
        latest_version = requests.post("http://adp.nekocode.top/update/version.php").json()['version']
    except:
        return None
    if latest_version == f"{major}.{minor}.{patch}":
        return True
    else:
        return latest_version


def get_notice_board():
    request = ""
    try:
        request = '\n'.join(requests.get("http://adp.nekocode.top/notice/get.php").json())
    except:
        pass
    return request

