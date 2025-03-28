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

| Name | Inheritance Path | Parameters | Purpose |
| --- | --- | --- | --- |
| GetLive2D | subscribe.Live2D | N/A | Get Live2D attributes (Live2D For Python) |
| GetWindowPosition | subscribe.Window | N/A | Get the relative position of the current desktop pet |
| GetCharacter | subscribe.Character | N/A | Get the currently selected character |
| GetName | subscribe.Character | N/A | Get the alias of the character |
| GetVoiceModel | subscribe.Model | N/A | Obtain the voice model |

| Name | Inheritance Path | Parameters | Purpose |
| --- | --- | --- | --- |
| InsertInterface | subscribe.views.Setting | *widget: QWidget* *icon: FluentIcon* *text: str* | Insert a tab interface into the settings panel. |

### InsertInterface (subscribe.views.Setting)

- widget: A QWidget-inherited interface needs to reference setObjectName to be displayed.
- icon: A FluentIcon
- text: Display text

| Name | Inheritance Path | Parameters | Purpose |
| --- | --- | --- | --- |
| SetDragAction | subscribe.actions.Register | *func: callable* | Set a MIME drag-and-drop event for the program (execute corresponding function upon mouse drag-and-drop) |
| SetClickAction | subscribe.actions.Register | *func: callable* | Set a click event for the program (execute corresponding function when clicking on the desktop pet) |
| SetMouseDragAction | subscribe.actions.Register | *func: callable* | Set a mouse drag event for the program (execute corresponding function when dragging the desktop pet) |
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

