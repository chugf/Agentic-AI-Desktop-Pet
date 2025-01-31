<div align="center">
    <h1 style="margin: 0;">人工智能桌面宠物</h1>
    <b><a href="README.md">English</a></b>
    <b> | </b>
    <b><a href="README_zh.md">简体中文</a></b>
    <b> | </b>
    <b><a href="README_ja.md">日本語</a></b>
</div>

# 简介

这是一个利用人工智能与用户互动的桌面宠物。

> 开发者：**可能会有点 *无聊*...**？

# 优点

**我们有一些与其他桌面宠物*不同* 的地方。**

### 人工智能

- 人工智能交互

> 您可以通过文本和语音进行对话。

- 人工智能代理

> 人工智能可以使用开发者编写的函数来操作您的电脑。
>
> 人工智能甚至可以捕获您的屏幕以查看您正在做的事情。

### 资源加载器

- Live2D模型

> 我使用Live2D引擎展示并创建模型，以获得最佳体验。

### 安全与定制

- 定制

> 您可以自定义模型、效果、声音、AI推理方式，甚至可以替换AI模型。

# Artificial Intelligence Inference Replace

**人工智能推理方式有2种**

- 本地推理 (这意味着您需要编写人工智能的API)

> 本地推理方式需要您的计算机至少1张GPU才能运行AI
> 
> 根据人工智能创作者，GPU数量至少为2。

- 云端推理 (这意味着您需要云端API)

### 本地模型推理要求

> 注意: 如果你的电脑不能达到最低要求，您可以选择云推理模式
>
> 均需要输入阿里云API-key和讯飞云API-id, API-secret。您可以获得完整的体验。

人工智能推理要求 *CUDA Runtime*

|     模型      |      模型最低要求      |        模型最低GPU要求        |      模型推荐要求      |         模型推荐GPU要求         |                用途                |
|:-----------:|:----------------:|:-----------------------:|:----------------:|:-------------------------:|:--------------------------------:|
| Qwen-Turbo  | 16GB CUDA memory | NVIDIA GeForce RTX 3060 | 20GB CUDA memory |  NVIDIA GeForce RTX 3090  |   It is used to generate text    |
| Qwen-VL-Max | 12GB CUDA memory |     NVIDIA RTX 2080     | 18GB CUDA memory | NVIDIA GeForce RTX 2080ti | It is used to understand picture |             |        1GB CUDA memory        |   NVIDIA GeForce GTX 650    | It is used to recognize speech |
| GPT_SoVITS  | 4GB CUDA memory  | NVIDIA GeForce RTX 1060 | 6GB CUDA memory  |  NVIDIA GeForce RTX 2060  |       It is used to speak        |
|   Whisper   |    Intel CPU     |           N/A           | 1GB CUDA memory  |  NVIDIA GeForce GTX 650   |  It is used to recognize speech  |

> 开发者的显卡算力服务器拥有7张显卡

# 模型替换

## 步骤

**您可以通过以下步骤替换模型：**

1. *下载* 您喜欢的模型。
2. *编辑* JSON文件如示例所示（Vanilla.json）
3. *右键点击* 原始模型并选择 `更改角色` -> `<选择自己的模型>`
4. *重新加载* 程序

## Json 文件格式

基础

```textmate
name        :         $ .string （显示名称及语音调用名称）
voice_model :         $ .string （语音模型名称 (GSV)）
default     :         $ .string （程序启动时首先加载的模型）
```

高级

|               对象                |             值*              |  类型  | 使用说明         |
|:-------------------------------:|:---------------------------:|:----:|--------------|
|    model.\<YourModel>.adult     |        AdultContent         | dict | 判断模型是否支持成人内容 |
|    model.\<YourModel>.adult     |      AdultLevelMinimum      | dict | 成人等级最低要求     |
|    model.\<YourModel>.adult     |      AdultLevelMaximum      | dict | 成人等级最高要求     |
|    model.\<YourModel>.adult     |        AdultDescribe        | dict | 成人描述         |
| model.\<YourModel>.adult.action | Action\<DescribeEnglish>[1] | list | 可使用的成人动作     |
| model.\<YourModel>.adult.voice  | Voice\<DescribeEnglish>[2]  | list | 想要播放的成人声音    |
|    model.\<YourModel>.action    |        [TableAction]        | dict | 可用的通用动作      |
|    model.\<YourModel>.voice     |        [TableVoice]         | dict | 想要播放的通用声音    |

1. AdultDescribe English (这意味着你的描述必须包含英文)
2. AdultDescribe English (这意味着你的描述必须包含英文)

### 表格 动作

|       动作        |   参数    |   类型    | 描述              |
|:---------------:|:-------:|:-------:|:----------------|
| ActionTouchHead |  param  | String  | Live2D参数调用      |
| ActionTouchHead | reverse | Boolean | 检查是否需要以逆序执行拼接动画 |
| ActionTouchHead |  play   | String  | VoiceTable键     |

### 表格 声音

|    声音    |  类型  | 描述              |
|:--------:|:----:|:----------------|
| coquetry | List | 撒娇的声音           |
|  happy   | List | 快乐的声音           |
|   sad    | List | 悲伤的声音           |
|  stable  | List | 平稳的声音（常用）       |
| welcome  | List | 用于欢迎用户的开始程序时的声音 |

## Json 文件解释

```json
{
  "settings.compatibility": "录屏兼容 Capture Compatibility",
  "settings.disable": {
    "rec": "语音识别 Speech Recognition",
    "trans": "自动翻译 Auto Translate",
    "online": "在线搜索 Search Online",
    "media": "图片/视频理解 Picture/Video Understanding",
    "voice": "AI TTS",
    "gmpene": "全局鼠标穿透 Global Mouse Penetration"
  },
  "settings.penetration": {
    "enable": "是否启用穿透",
    "start": "穿透被禁用的时间"
  }
}
```

# 引用开源库

![live2d](https://raw.githubusercontent.com/Arkueid/live2d-py/ba7fe4a70a77f62300e600ff56eaf59231cbb80f/docs/logo.svg)
- [Live2D-Py](https://github.com/Arkueid/live2d-py)

![PyOpenGL](https://ts1.cn.mm.bing.net/th/id/R-C.84b5fa1a7e2f46924f0a94c474476255?rik=lzp8Bgb3Sw5r8g&riu=http%3a%2f%2fcdn.wolfire.com%2fblog%2fprototype%2fopengl2.png&ehk=UETJyty3s3whP70x%2ff9WOe0dIcQ%2fbLzohetW%2fwEZqUc%3d&risl=&pid=ImgRaw&r=0)
- [PyOpenGL](https://github.com/mcfletch/pyopengl.git)

![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
- [Python](https://github.com/python/cpython.git)

- [PyQt5](https://github.com/PyQt5/PyQt.git)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg.git)


