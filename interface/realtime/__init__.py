"""
@Author:  HeavyNotFat
@Idea: 由服务端接受请求后交给interface.subscribe进行解析
@Usage:
   客户端必须为UDP协议！
   客户端必须为UDP协议！
   客户端必须为UDP协议！

   客户端接受最少2个参数，采用JSON
      instance        $ string. 实例路径，以点分割
      parameter       $ dict | list. 传参，dict为点对点传参，list为顺序传参
   客户端接受最多3个参数，采用JSON
      instance        $ string. 继承实例路径，以点分割
      method          $ string. 调用实例方法
      parameter       $ dict | list. 传参，dict为点对点传参，list为顺序传参
   要求：
      1、 如果不穿入method，instance就传入全部的路径
      2、 如果传入method，instance就只传入继承路径
      3、 parameter如果为字典(dict)，字典的键为传入的参数名，对应的值为传入的参数值
      4、 parameter如果为列表(list)，就以传入的顺序传参
   示例：
      {
        "instance": "Character.GetName",
        "parameter": []
      }
      Character.GetName是实例路径
      和
      {
        "instance": "Character",
        "method": "GetName"
        "parameter": []
      }
      是等效的
      Character是继承路径，GetName是调用的实例方法

      这个等于
      interface.subscribe.Character.GetName()
"""
import socket
import json
import threading
from typing import Callable


class UDPServer:
    def __init__(self, host='0.0.0.0', port=8210, get_interface_answer: Callable | None = None):
        self.host = host
        self.port = port
        self.get_interface_answer = get_interface_answer
        self.server_socket = None
        self.running = False
        self.receive_thread = None

    def start(self):
        """启动UDP服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.running = True
        print(f"UDP Server started at {self.host}:{self.port}")

        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()

    def _receive_loop(self):
        """持续接收数据包"""
        while self.running:
            address = None
            try:
                data, address = self.server_socket.recvfrom(65535)
                interface_data = json.loads(data.decode('utf-8'))
                print(f"[{address}]: {interface_data}")

                if "method" in interface_data.keys():
                    calling = f"subscribe.{interface_data['instance']}.{interface_data['method']}"
                else:
                    calling = f"subscribe.{interface_data['instance']}"
                self.handle_message(self.get_interface_answer(
                    calling, interface_data['parameter']
                ), address)

            except Exception as e:
                if address is not None:
                    self.handle_message(f"Error: {e}", address)

    def handle_message(self, callback, address):
        """处理客户端消息"""
        self.server_socket.sendto(callback.encode('utf-8'), address)

    def stop(self):
        """停止服务端"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
