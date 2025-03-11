# README.md

<div align="center">
    <h1 style="margin: 0;">AI Desktop Companion</h1>
    <br/>
    <b><a href="README.md">English</a></b> | <b><a href="README_zh.md">简体中文</a></b>
    <br/>
</div>

---

> [!CAUTION]
> The program is scheduled to undergo an architectural reconstruction starting from March 14, 2025. After the reconstruction, the architecture will be updated to `Version 3 (Active&Beauty)`. Please note that the new architecture may not be backward compatible with the previous versions...
>
> The update will transition the architectural version from `Version 2 (Loader&Processor)` to `Version 3 (Active&Beauty)`
> 
> The program version will be upgraded from `Stable Version 2.1.1` to `Stable Version 2.2.0`.

---


## 🌟 Project Overview

This is an AI-driven desktop pet application that supports highly customizable character appearances, animations, and
conversation features. It can interact with users through voice recognition and respond in real-time to touch
operations. Whether you are a tech enthusiast or a regular user, you can easily get started and enjoy a personalized
experience.

> [!NOTE]
> This is not just a desktop pet, but your digital assistant!

---

## 🚀 Key Features

- **Intelligent Conversation**  
  Based on advanced AI technology, it achieves lively and natural conversational interactions.

- **Fully Open Source**  
  Open source, secure, and stable! Transparent code, contributions welcome.

- **Multilingual Support**  
  Supports Chinese, English, Japanese, and other languages, with easy expansion for additional languages.

- **Highly Customizable**  
  Customize character models, animations, sounds, conversations, and more to create a unique desktop companion.

- **Plugin System**  
  Provides rich plugins and API interfaces to make your AI smarter and more flexible.

---

## 🛠 Usage Guide

### Adding Models

1. Download your favorite Live2D model files.
2. Place the files in the `resources/model` directory.
3. Restart the program to load the new model.

> **Tip**: If model replacement fails, ensure that the model data is bound (`Binding Settings -> Animation Binding`).

### Binding Settings

#### Extension Tools

Extension tools allow you to define new function call capabilities for the AI. For example:

```python 
def process_human_information(name: str, age: int, gender: str):
    """ Example function to process human information. """
    return "Processing Complete!"
```

#### Plugin Development

Using built-in API interfaces, you can quickly develop plugins. Here are some commonly used APIs:

| API Name          | Inheritance Path    | Parameters | Description                              |
|-------------------|---------------------|------------|------------------------------------------|
| GetLive2D         | subscribe.Live2D    | null       | Get Python properties of Live2D model    |
| GetWindowPosition | subscribe.Window    | null       | Get window position                      |
| GetCharacter      | subscribe.Character | null       | Get the name of the current Live2D model |
| GetName           | subscribe.Character | null       | Get character name                       |
| GetVoiceModel     | subscribe.Model     | null       | Get voice model name                     |

| API Name       | Inheritance Path        | Parameters  | Description      |
|----------------|-------------------------|-------------|------------------|
| InsertNotebook | subscribe.views.Setting | frame, text | 插入一个Frame进设置的选项卡 |
| DeleteNotebook | subscribe.views.Setting | frame       | 删除一个Frame的选项卡    |

---

## 📦 Supported External Libraries

The following is a list of core libraries this project depends on:

| Library Name     | Version |
|------------------|---------|
| pyqt5            | latest  |
| pyopengl         | latest  |
| pypiwin32        | latest  |
| live2d-py        | latest  |
| dashscope        | latest  |
| markdown         | latest  |
| requests         | latest  |
| pyaudio          | latest  |
| numpy            | latest  |
| websocket-client | latest  |
| mss              | latest  |
| pydantic         | latest  |
| uvicorn          | latest  |
| fastapi          | latest  |

---

## 🎯 Feature Checklist

- [x] Live2D Model Support
- [x] AI Conversation Engine
- [x] Multimodal AI Support
- [x] Hot Reload Models
- [x] Plugin System
- [ ] Full Cloud Support
- [ ] Additional International Languages

---

## 💡 Detailed Highlights

- **Tooltip**: Displays detailed descriptions when hovering over elements.
- **Shader Optimization**: Optimized for older devices.
- **Taskbar Compatibility**: Pet stays within taskbar boundaries.
- **Multilingual Expansion**: Easily add support for new languages.

---

## 🙏 Acknowledgments

Thank you to the following open-source projects for their contributions:

- [Live2D-Py](https://github.com/Arkueid/live2d-py)
- [PyOpenGL](https://github.com/mcfletch/pyopengl.git)
- [Python](https://github.com/python/cpython.git)
- [PyQt5](https://github.com/PyQt5/PyQt.git)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg.git)

---

## 🤝 Contribution Guidelines

Welcome to submit Issues or Pull Requests! Let's make this project even better together!

---

## 📜 License

This project is licensed under the GPLv3.0 License. See the [LICENSE](./LICENSE) file for details.

