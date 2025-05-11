<div align="center">
    <h2>简体中文 API 文档</h2>
    <h3>⚠️ Because author is a Chinese, so this document is written in Chinese.</h3>
    <h3>🌸 If you have enough energy, please help me translate it into more language.</h3>
</div>

# API 接口 说明

> [!WARNING]
> API 接口 主要说明为 订阅(subscribe) API 的文档

> [!WARNING]
> 实时API (realtime) 用法和subscribe语法相同，但依赖Socket套字节UDP协议运行

# 实时 API

> [!NOTE]
> 此专为 `独立程序` 设计，**程序增强请使用 `订阅(subscribe) API`**

其继承**完全参照** [订阅(subscribe)](#订阅API) API 的文档

传入参数时就是将interface去掉

可将下面的代码嵌入你的本体代码中

```python
import socket
import json
import threading


class RealtimeAPI(threading.Thread):
    def __init__(self, interface, address=('127.0.0.1', 8210)):
        """
        初始化UDP客户端线程
        :param interface: 必填
        :param address: 服务器地址，默认为 ('127.0.0.1', 8210)
        """
        super().__init__()
        self.address = address
        self.interface = interface
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send_request(self, message_dict):
        self.client_socket.sendto(json.dumps(message_dict).encode('utf-8'), self.address)

        response, server_address = self.client_socket.recvfrom(1024)
        response_data = None if response.decode('utf-8') == "None" else response.decode('utf-8')

        print(f"[{self.address[0]}:{self.address[1]}] Return Response: {response_data}")
        return response_data

    def run(self):
        """
        线程启动时执行的方法
        """
        try:
            self._send_request(self.interface)
        finally:
            self.client_socket.close()

```

## interface要求

1. 如果不传入method，instance就传入全部的路径
2. 如果传入method，instance就只传入继承路径
3. parameter如果为字典(dict)，字典的键为传入的参数名，对应的值为传入的参数值
4. parameter如果为列表(list)，就以传入的顺序传参

---

使用时写入 
```python
RealtimeAPI(
    {'instance': '', 
     'method': '', 
     'parameter': []
})
```

最后在`start()`即可

例如：

```python
RealtimeAPI({
    "instance": "subscribe.Character",
    "method": "GetName",
    "parameter": []
}).start()
```

## 高级调用

```python
RealtimeAPI({
    "instance": "setting.customize.widgets",
    "method": "pop_notification",
    "parameter": ["RealtimeAPI 实例", "setting interface 调用成功！", "success"]
}).start()
```

---

# 订阅API

> [!NOTE]
> 此专为 `程序增强` 设计，**独立程序请使用 `实时(realtime) API`**

使用时请写入

```javascript
interface.subscribe.<InterfaceBelow>
```

## 基础 API

### Character

#### GetCharacter

> 用于获取角色模型名称 

传入参数：

- 无参数

返回值：

- **`name`**: `str` 字符串类型

#### GetName

> 获取用户给角色取的名字
 
传入参数：

- 无参数

返回值：

- **`name`**: `str` 字符串类型

### Live2D

#### GetLive2D

> 获取程序内部的Live2D属性，参照[Live2D-PY](https://github.com/Arkueid/live2d-py)

传入参数：

- 无参数

返回值：

- **`attr`**: `live2d.LAppModel` [Live2D-PY](https://github.com/Arkueid/live2d-py) 中的LAppModel类型

### Model

#### GetVoiceModel

> 获取选择的语音模型

传入参数：

- 无参数

返回值：

- **`voice_name`**: `str` 字符串类型

### Window

#### GetWindowPosition

> 获取窗口位置

传入参数：

- 无参数

返回值：

- **`position`**: `tuple` 字符串类型
  - width: `int` 窗口宽度
  - height: `int` 窗口高度
  - x: `int` 窗口x坐标
  - y: `int` 窗口y坐标

## 视图 View API

## 截断 Hooks API

## 行为 Actions API

## 交互 Interact API

## 标准常量 Standards API
