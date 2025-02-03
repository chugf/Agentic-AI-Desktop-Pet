```markdown
<div align="center">
    <h1 style="margin: 0;">Artificial Intelligence Desktop Companion</h1>
    <b><a href="README.md">English</a></b>
    <b> | </b>
    <b><a href="README_zh.md">简体中文</a></b>
    <b> | </b>
    <b><a href="README_ja.md">日本語</a></b>
</div>

# Introduction

This project introduces an innovative desktop companion powered by artificial intelligence, designed to interact seamlessly with users.

> Developer's Note: **Perhaps it's a touch *unconventional*...**?

# Unique Features

**Our desktop companion stands out with distinctive features.**

### Advanced AI Integration

- Interactive AI Communication

> Engage in conversations through both text and voice interfaces.

- AI-Powered Assistance

> The AI can perform tasks on your computer using predefined functions.
>
> It can even monitor your screen to understand your current activities.

### Dynamic Resource Management

- Live2D Integration

> Utilizing the Live2D Engine, we provide an immersive experience with dynamic models.

### Security and Personalization

- Extensive Customization

> Tailor the companion's appearance, effects, voice, AI behavior, and even replace the underlying AI model.

# AI Inference Options

**Choose between two AI inference methods:**

- Local Inference (Requires running an AI API on your computer)

> Local inference demands at least 1 GPU.
>
> The AI developer recommends a minimum of 2 GPUs for optimal performance.

- Cloud Inference (Utilizes cloud-based APIs)

### Local Inference Specifications

> Note: If your system doesn't meet the minimum requirements, opt for cloud inference.
> 
> Simply input your Aliyun API-key and XunfeiYun API credentials to enjoy a comparable experience to local inference.

AI inference necessitates *CUDA Runtime*

|    MODEL    | Minimum Model Requirements | Minimum GPU Requirements | Recommended Model Requirements | Recommended GPU Requirements |              Application               |
|:-----------:|:--------------------------:|:------------------------:|:-----------------------------:|:---------------------------:|:--------------------------------------:|
| Qwen-Turbo  |      16GB CUDA memory      | NVIDIA GeForce RTX 3060  |       20GB CUDA memory        |   NVIDIA GeForce RTX 3090   |   Text generation                      |
| Qwen-VL-Max |      12GB CUDA memory      |     NVIDIA RTX 2080      |       18GB CUDA memory        |  NVIDIA GeForce RTX 2080ti  | Image comprehension                    |
| GPT_SoVITS  |      4GB CUDA memory       | NVIDIA GeForce RTX 1060  |        6GB CUDA memory        |   NVIDIA GeForce RTX 2060   | Speech synthesis                       |
|   Whisper   |         Intel CPU          |           N/A            |        1GB CUDA memory        |   NVIDIA GeForce GTX 650    | Speech recognition                     |

> The developer's GPU server is equipped with 7 GPUs.

# Model Customization

## Steps

**Follow these steps to customize your model:**

1. *Download* your preferred model.
2. *Edit* the JSON file following the example (Vanilla.json).
3. *Right-click* the original model and select `Change Character` -> `<Choose your own model>`.
4. *Restart* the application.

## JSON File Structure

Basic

```textmate
name        :         $ .string (Display and voice call name)
voice_model :         $ .string (Voice model name (GSV))
default     :         $ .string (Initial model loaded at program start)
```

Advanced

|             Object              |           value*            | type | Description                                    |
|:-------------------------------:|:---------------------------:|:----:|------------------------------------------------|
|    model.\<YourModel>.adult     |        AdultContent         | dict | Indicates if the model supports adult content  |
|    model.\<YourModel>.adult     |      AdultLevelMinimum      | dict | Minimum adult content level                    |
|    model.\<YourModel>.adult     |      AdultLevelMaximum      | dict | Maximum adult content level                    |
|    model.\<YourModel>.adult     |        AdultDescribe        | dict | Description of adult content                   |
| model.\<YourModel>.adult.action | Action\<DescribeEnglish>[1] | list | List of adult actions                          |
| model.\<YourModel>.adult.voice  | Voice\<DescribeEnglish>[2]  | list | List of adult voices                           |
|    model.\<YourModel>.action    |        [TableAction]        | dict | Common actions                                 |
|    model.\<YourModel>.voice     |        [TableVoice]         | dict | Common voices                                  |

1. AdultDescribe in English (Descriptions must include English).
2. AdultDescribe in English (Descriptions must include English).

### Action Table

|     action      |  param  |  type   | Description                                                          |
|:---------------:|:-------:|:-------:|:----------------------------------------------------------------------|
| ActionTouchHead |  param  | String  | Live2D parameter call                                                |
| ActionTouchHead | reverse | Boolean | Determines if animations should play in reverse                      |
| ActionTouchHead |  play   | String  | VoiceTable key for the action                                         |

### Voice Table

|  voice   | type | Description                                                     |
|:--------:|:----:|:-----------------------------------------------------------------|
| coquetry | List | Coquettish voice clips                                           |
|  happy   | List | Happy voice clips                                                |
|   sad    | List | Sad voice clips                                                  |
|  stable  | List | Neutral voice clips (Common)                                     |
| welcome  | List | Welcome voice clips played at program start                      |

## JSON File Example

```json
{
  "settings.compatibility": "Screen Capture Compatibility",
  "settings.disable": {
    "rec": "Speech Recognition",
    "trans": "Auto Translate",
    "online": "Online Search",
    "media": "Image/Video Comprehension",
    "voice": "AI TTS",
    "gmpene": "Global Mouse Penetration"
  },
  "settings.penetration": {
    "enable": "Enable Penetration",
    "start": "Time to Disable Penetration"
  }
}
```

# Acknowledgments

![live2d](https://raw.githubusercontent.com/Arkueid/live2d-py/ba7fe4a70a77f62300e600ff56eaf59231cbb80f/docs/logo.svg)
- [Live2D-Py](https://github.com/Arkueid/live2d-py)

![PyOpenGL](https://ts1.cn.mm.bing.net/th/id/R-C.84b5fa1a7e2f46924f0a94c474476255?rik=lzp8Bgb3Sw5r8g&riu=http%3a%2f%2fcdn.wolfire.com%2fblog%2fprototype%2fopengl2.png&ehk=UETJyty3s3whP70x%2ff9WOe0dIcQ%2fbLzohetW%2fwEZqUc%3d&risl=&pid=ImgRaw&r=0)
- [PyOpenGL](https://github.com/mcfletch/pyopengl.git)

![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
- [Python](https://github.com/python/cpython.git)

- [PyQt5](https://github.com/PyQt5/PyQt.git)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg.git)
```
