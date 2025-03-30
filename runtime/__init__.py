# 为外部导入做好准备
from . import thread
from . import file

import os
import tempfile
import ast
import threading
import time
import re
import struct

import mss
import requests
import win32api
import win32con
import numpy


class PassedNoneContent(object):
    pass


SENSITIVE_CONTENT = [
    "/resources/configure.json",
    PassedNoneContent(),  # 占位符
    PassedNoneContent(),  # 占位符
]
major = "3"
minor = "0"
patch = "0"


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
                if full_call_path[0] == "interface":
                    self.called[0] = True
                if full_call_path[0] == "interface" and full_call_path[2] == "views":
                    self.called[1] = True
                if full_call_path[0] == "interface" and full_call_path[2] == "actions":
                    self.called[2] = True
        self.generic_visit(node)


class PythonCodeExaminer(ast.NodeVisitor):
    """
    内容审计 用于检查插件代码安全（用户可以自行开启）
    开启：死循环检测 (无法关闭)
    分为5个等级:
     L1: 轻微保护（
                    仅审计读取./resources/configure.json
                用户自行判断是否运行）
     L2: 轻度保护（
                    仅审计读取./resources/configure.json文件。
                    有支持有云访问能力的插件。
                用户自行判断是否运行）
     L3: 中度保护（
                    审计以上内容
                    是否调用(
                        exec, eval
                    )，
                程序先阻止运行用户可以手动运行）
     L4: 高度保护（
                    审计所有内容
                    库导入内容(
                        os, sys
                    )
                程序直接阻止，无法运行）
     L5: 重度保护（
                    审计所有内容
                    库导入内容(
                        pickle, subprocess, shutil,
                        importlib, ctypes, cffi
                    )，
                程序直接阻止，无法运行）
    """
    def __init__(self, code):
        self.code = code
        self.exists = [False] * 10
        self.code_optimise = [False] * 10
        self.imported_modules = set()
        self.analyze()

    def analyze(self):
        code = re.sub(r'^.*interface\.subscribe.*$\n?', '', self.code, flags=re.MULTILINE)
        tree = ast.parse(code)
        self.visit(tree)

    # 判断
    @property
    def is_l1(self):
        return self.is_quoted_config

    @property
    def is_l2(self):
        return self.is_l1 or self.is_imported_requests or self.is_imported_websocket

    @property
    def is_l3(self):
        return self.is_l2 or self.is_called_execute_or_evaluate

    @property
    def is_l4(self):
        return self.is_l3 or self.is_imported_os_or_sys

    @property
    def is_l5(self):
        return self.is_l4 or \
                self.is_imported_ctypes_or_cffi or self.is_imported_pickle or self.is_imported_subprocess or \
                self.is_imported_shutil, self.is_imported_importlib

    # 代码优化建议
    @property
    def optimize_infinite_loop(self):
        return self.code_optimise[0]

    # 子
    @property
    def is_quoted_config(self):
        return self.exists[0]

    @property
    def is_called_execute_or_evaluate(self):
        return self.exists[1]

    @property
    def is_called_compile(self):
        return self.exists[2]

    @property
    def is_imported_websocket(self):
        return "websocket" in self.imported_modules

    @property
    def is_imported_requests(self):
        return "requests" in self.imported_modules

    @property
    def is_imported_os_or_sys(self):
        return "os" in self.imported_modules or "sys" in self.imported_modules

    @property
    def is_imported_ctypes_or_cffi(self):
        return "ctypes" in self.imported_modules or "cffi" in self.imported_modules

    @property
    def is_imported_pickle(self):
        return "pickle" in self.imported_modules

    @property
    def is_imported_subprocess(self):
        return "subprocess" in self.imported_modules

    @property
    def is_imported_shutil(self):
        return "shutil" in self.imported_modules

    @property
    def is_imported_importlib(self):
        return "importlib" in self.imported_modules

    def custom_examine_library(self, module):
        return module in self.imported_modules

    def visit_Call(self, node):
        """审计函数调用"""
        if isinstance(node.func, ast.Name):
            if node.func.id == 'exec':
                self.exists[1] = True
            elif node.func.id == 'eval':
                self.exists[1] = True
            elif node.func.id == 'compile':
                self.exists[2] = True
        self.generic_visit(node)

    def visit_Str(self, node):
        """审计字符串"""
        for index, content in enumerate(SENSITIVE_CONTENT):
            if content in node.s:
                self.exists[index] = True
        self.generic_visit(node)

    def visit_Constant(self, node):
        """审计字符串"""
        if isinstance(node.value, str):
            for index, content in enumerate(SENSITIVE_CONTENT):
                if isinstance(content, PassedNoneContent):
                    continue
                if content in node.value:
                    self.exists[index] = True
        self.generic_visit(node)

    def visit_Import(self, node):
        """审计 以import导入的库"""
        for alias in node.names:
            self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """审计 以from导入的库"""
        if node.module:
            self.imported_modules.add(node.module)
        self.generic_visit(node)

    def visit_While(self, node):
        """审计 while关键字是否存在死循环"""
        is_condition = False
        if isinstance(node.test, ast.Constant) and node.test.value in (True, 1):
            is_condition = True
        elif isinstance(node.test, ast.NameConstant) and node.test.value is True:
            is_condition = True
        if is_condition:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.code_optimise[0] = True
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


def get_policy():
    request = ""
    try:
        request = '\n'.join(requests.get("http://adp.nekocode.top/notice/get_policy.php").json())
    except:
        pass
    return request


def user_register(email):
    try:
        register_response = requests.post("http://adp.nekocode.top/account/register.php", json={'to': email})
        if register_response.json().get('error'):
            return {"status": False, "message": register_response.json()['error']}
        elif register_response.json().get('success'):
            return {"status": True, "message": register_response.json()['success']}
    except:
        return {"status": False, "message": "发送邮件错误！"}


def user_vertify(email, code, password):
    try:
        vertify_response = requests.post("http://adp.nekocode.top/account/vertify.php",
                                         json={'email': email, 'code': code, 'password': password})
        if vertify_response.json().get('error'):
            return {"status": False, "message": vertify_response.json()['error']}
        elif vertify_response.json().get('success'):
            return {"status": True, "message": vertify_response.json()['success']}
    except:
        return {"status": False, "message": "验证错误！"}


def user_login(email, password):
    try:
        login_response = requests.post("http://adp.nekocode.top/account/login.php",
                                       json={'email': email, 'password': password})
        if login_response.json().get('error'):
            return {"status": False, "message": login_response.json()['error']}
        elif login_response.json().get('success'):
            return {"status": True, "message": login_response.json()['success']}
    except:
        return {"status": False, "message": "登录错误！"}


def find_internal_recording_device(p):
    """寻找内录设备"""
    target = '立体声混音'
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['name'].find(target) >= 0 and dev_info['hostApi'] == 0:
            return i
    return -1


def calculate_rms(data):
    """计算RMS音量标准"""
    length = len(data) / 2
    shorts = struct.unpack("%dh" % length, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    rms = numpy.sqrt(sum_squares / length)
    return rms * 1000
