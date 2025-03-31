# README.md

<div align="center">
    <h1 style="margin: 0;">AI Desktop Companion</h1>
    <br/>
    <b><a href="README.md">English</a></b> | <b><a href="README_zh.md">简体中文</a></b>
    <br/>
</div>

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

### Extension Tools

Extension tools allow you to define new function call capabilities for the AI. For example:

```python 
def process_human_information(name: str, age: int, gender: str):
    """ Example function to process human information. """
    return "Processing Complete!"
```

### Plugin Development

Using built-in API interfaces, you can quickly develop plugins. Here are some commonly used APIs:

| API Name          | Inheritance Path              | Parameters | Description                              |
|-------------------|-------------------------------|------------|------------------------------------------|
| GetLive2D         | interface.subscribe.Live2D    | N/A        | Get Python properties of Live2D model    |
| GetWindowPosition | interface.subscribe.Window    | N/A        | Get window position                      |
| GetCharacter      | interface.subscribe.Character | N/A        | Get the name of the current Live2D model |
| GetName           | interface.subscribe.Character | N/A        | Get character name                       |
| GetVoiceModel     | interface.subscribe.Model     | N/A        | Get voice model name                     |

| API Name        | Inheritance Path                  | Parameters         | Description                          |
|-----------------|-----------------------------------|--------------------|--------------------------------------|
| InsertInterface | interface.subscribe.views.Setting | widget, icon, text | Insert widget into setting interface |
| DeleteInterface | interface.subscribe.views.Setting | widget             | Delete widget from setting interface |

#### InsertInterface

- **widget**: The widget must ***setObjectName***

> QWidget
>
> This parameter is a widget that will be inserted into the setting interface.

- icon

> FluentIcon
>
> This parameter is the icon displayed in the setting interface.

- text

> str
>
> This parameter is the text displayed in the setting interface.

#### DeleteInterface

- widget

> QWidget
>
> This parameter is the widget that will be deleted from the setting interface.

| API Name           | Inheritance Path                     | Parameters     | Description                                                  |
|--------------------|--------------------------------------|----------------|--------------------------------------------------------------|
| SetDragAction      | interface.subscribe.actions.Register | func: callable | When pet is moving, it will call                             |
| SetClickAction     | interface.subscribe.actions.Register | func: callable | When pet is clicked, it will call                            |
| SetMouseDragAction | interface.subscribe.actions.Register | func: callable | When pet is dragged, it will call                            |                                |
| SetAIOutput        | interface.subscribe.actions.Register | func: callable | When the AI(*Only Reasoning AI*) is outputting, it will call |                   |

#### SetDragAction

- *RawQMimeData*: It will return the raw `QMimeData` data
- *AnalyzedData*: It will return the program analyzed data

#### SetClickAction

- N/A

#### SetMouseDragAction

- *CurrentMouseX*: It will return current mouse X coordinate
- *CurrentMouseY*: It will return current mouse Y coordinate
- *CurrentMainWindowX*: It will return the current main window X coordinate
- *CurrentMainWindowY*: It will return the current main window Y coordinate

#### SetAIOutput

- *Answer*: It will return the AI answer
- *IsLast*: It will return whether it is the last answer

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

