<div align="center">
    <h1 style="margin: 0;">人工智能桌面伴侣</h1>
    <b><a href="README.md">English</a></b>
    <b> | </b>
    <b><a href="README_zh.md">简体中文</a></b>
</div>

# 介绍

本项目推出了一款创新的人工智能桌面伴侣，旨在与用户无缝互动。

> 开发者注：**或许它有点与众不同...**？

# 独特功能

**我们的桌面伴侣具有以下独特功能。**

### 高级人工智能集成

- 交互式人工智能对话

> 通过文本和语音界面进行对话。

- 人工智能辅助功能

> 人工智能可以通过预定义的功能在您的计算机上执行任务。
>
> 它甚至可以监控您的屏幕以了解您当前的活动。

### 动态资源管理

- Live2D 集成

> 利用 Live2D 引擎，我们提供了动态模型的沉浸式体验。

### 安全性与个性化

- 广泛的自定义选项

> 定制伴侣的外观、效果、语音、AI 行为，甚至替换底层 AI 模型。

# AI 推理选项

**选择两种 AI 推理方式：**

- 本地推理（需要在您的计算机上运行 AI API）

> 本地推理需要至少 1 个 GPU。
>
> AI 开发者建议至少 2 个 GPU 以获得最佳性能。

- 云端推理（使用基于云的 API）

### 本地推理规格

> 注意：如果您的系统不满足最低要求，请选择云端推理。
> 
> 只需输入您的阿里云 API-key 和讯飞云 API 凭证，即可享受与本地推理相当的体验。

AI 推理需要 *CUDA 运行时*

|    模型    | 最低模型要求 | 最低 GPU 要求 | 推荐模型要求 | 推荐 GPU 要求 |              应用场景              |
|:----------:|:------------:|:-------------:|:------------:|:-------------:|:----------------------------------:|
| Qwen-Turbo |  16GB CUDA 内存 | NVIDIA GeForce RTX 3060 | 20GB CUDA 内存 | NVIDIA GeForce RTX 3090 |   文本生成                         |
| Qwen-VL-Max|  12GB CUDA 内存 | NVIDIA RTX 2080 | 18GB CUDA 内存 | NVIDIA GeForce RTX 2080ti | 图像理解                           |
| GPT_SoVITS |  4GB CUDA 内存  | NVIDIA GeForce RTX 1060 | 6GB CUDA 内存  | NVIDIA GeForce RTX 2060 | 语音合成                           |
| Whisper    |  Intel CPU     | N/A           | 1GB CUDA 内存  | NVIDIA GeForce GTX 650 | 语音识别                           |

> 开发者的 GPU 服务器配备了 7 个 GPU。

# 模型自定义

## 步骤

**按照以下步骤自定义您的模型：**

1. *下载* 您喜欢的模型。
2. *编辑* JSON 文件，参考示例 (Vanilla.json)。
3. *右键单击* 原始模型并选择 `更换角色` -> `<选择您的模型>`。
4. *重启* 应用程序。

## JSON 文件结构

基础

```textmate
name        :         $ .string (显示和语音调用的名称)
voice_model :         $ .string (语音模型名称 (GSV))
default     :         $ .string (程序启动时加载的初始模型)
```

高级

|             对象              |           值*            | 类型 | 描述                                    |
|:-----------------------------:|:------------------------:|:----:|-----------------------------------------|
|    model.\<YourModel>.adult     |        AdultContent         | 字典 | 指示模型是否支持成人内容                |
|    model.\<YourModel>.adult     |      AdultLevelMinimum      | 字典 | 成人内容的最低级别                      |
|    model.\<YourModel>.adult     |      AdultLevelMaximum      | 字典 | 成人内容的最高级别                      |
|    model.\<YourModel>.adult     |        AdultDescribe        | 字典 | 成人内容的描述                          |
| model.\<YourModel>.adult.action | Action\<DescribeEnglish>[1] | 列表 | 成人动作列表                            |
| model.\<YourModel>.adult.voice  | Voice\<DescribeEnglish>[2]  | 列表 | 成人语音列表                            |
|    model.\<YourModel>.action    |        [TableAction]        | 字典 | 常见动作                                |
|    model.\<YourModel>.voice     |        [TableVoice]         | 字典 | 常见语音                                |

1. 成人描述需为英文（描述必须包含英文）。
2. 成人描述需为英文（描述必须包含英文）。

### 动作表

|     动作      |  参数  |  类型   | 描述                                                          |
|:-------------:|:------:|:-------:|:--------------------------------------------------------------|
| ActionTouchHead |  param  | 字符串  | Live2D 参数调用                                                |
| ActionTouchHead | reverse | 布尔值  | 确定动画是否应反向播放                                         |
| ActionTouchHead |  play   | 字符串  | 动作对应的 VoiceTable 键                                       |

### 语音表

|  语音   | 类型 | 描述                                                     |
|:-------:|:----:|:---------------------------------------------------------|
| coquetry | 列表 | 撒娇语音片段                                             |
|  happy   | 列表 | 开心语音片段                                             |
|   sad    | 列表 | 悲伤语音片段                                             |
|  stable  | 列表 | 中性语音片段（常见）                                     |
| welcome  | 列表 | 程序启动时播放的欢迎语音片段                             |

## JSON 文件示例

```json
{
  "settings.compatibility": "屏幕捕捉兼容性",
  "settings.disable": {
    "rec": "语音识别",
    "trans": "自动翻译",
    "online": "在线搜索",
    "media": "图像/视频理解",
    "voice": "AI 语音合成",
    "gmpene": "全局鼠标穿透"
  },
  "settings.penetration": {
    "enable": "启用穿透",
    "start": "禁用穿透的时间"
  }
}
```

# 致谢

![live2d](https://raw.githubusercontent.com/Arkueid/live2d-py/ba7fe4a70a77f62300e600ff56eaf59231cbb80f/docs/logo.svg)
- [Live2D-Py](https://github.com/Arkueid/live2d-py)

![PyOpenGL](https://ts1.cn.mm.bing.net/th/id/R-C.84b5fa1a7e2f46924f0a94c474476255?rik=lzp8Bgb3Sw5r8g&riu=http%3a%2f%2fcdn.wolfire.com%2fblog%2fprototype%2fopengl2.png&ehk=UETJyty3s3whP70x%2ff9WOe0dIcQ%2fbLzohetW%2fwEZqUc%3d&risl=&pid=ImgRaw&r=0)
- [PyOpenGL](https://github.com/mcfletch/pyopengl.git)

![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
- [Python](https://github.com/python/cpython.git)

- [PyQt5](https://github.com/PyQt5/PyQt.git)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg.git)
