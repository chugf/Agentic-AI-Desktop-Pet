<div align="center">
    <h1 style="margin: 0;">Artificial Intelligence Desktop Pet</h1>
    <b><a href="README.md">English</a></b>
    <b> | </b>
    <b><a href="README_zh.md">简体中文</a></b>
    <b> | </b>
    <b><a href="README_ja.md">日本語</a></b>
</div>

# Introduction

This is a desktop pet that uses artificial intelligence to interact with the user.

> Developer: **It might be a little *boring*...**?

# Benefits

**We have some *different* from other desktop pets.**

### Artificial Intelligence

- Artificial Intelligence Interaction

> You can have a dialogue by text and voice.

- Artificial Intelligence Agent

> The AI can operate you computer by the function developer wrote.
>
> The AI even can capture your screen to see what you are doing.

### Resources Loader

- Live2D Model

> I use Live2D Engine to show and make the model for getting the best experience.

### Safety and Customize

- Customize

> You can customize the model, the effects, the voice, the AI inference way, and even can replace the AI model.

# Model Replacer

## Steps

**You can replace the model by the following steps:**

1. *Download* model you like.
2. *Edit* The json file as the example (Vanilla.json)
3. *Right-click* the original model and choose `Change Character` -> `<Choose your own model>`
4. *Reload* the program

## Json File format

Basic

```textmate
name        :         $ .string (The show and voice calls name)
voice_model :         $ .string (The voice model name (GSV))
default     :         $ .string (When program start, the first load the model)
```

Advanced

|             Object              |           value*            | type | Usage                                    |
|:-------------------------------:|:---------------------------:|:----:|------------------------------------------|
|    model.\<YourModel>.adult     |        AdultContent         | dict | Know if the model is supported for adult |
|    model.\<YourModel>.adult     |      AdultLevelMinimum      | dict | " The Adult Level Minimum                |
|    model.\<YourModel>.adult     |      AdultLevelMaximum      | dict | The Adult Level Maximum                  |
|    model.\<YourModel>.adult     |        AdultDescribe        | dict | The Adult description                    |
| model.\<YourModel>.adult.action | Action\<DescribeEnglish>[1] | list | The Adult action that can be used        |
| model.\<YourModel>.adult.voice  | Voice\<DescribeEnglish>[2]  | list | The Adult voice that you want to play    |
|    model.\<YourModel>.action    |        [TableAction]        | dict | The common action that can be used       |
|    model.\<YourModel>.voice     |        [TableVoice]         | dict | The common voice that you want to play   |

1. AdultDescribe English (This means your describe must involve English)
2. AdultDescribe English (This means your describe must involve English)

### Table Action

|     action      |  param  |  type   | describe                                                          |
|:---------------:|:-------:|:-------:|:------------------------------------------------------------------|
| ActionTouchHead |  param  | String  | The Live2D param calls                                            |
| ActionTouchHead | reverse | Boolean | Check if you need to perform stitched animations in reverse order |
| ActionTouchHead |  play   | String  | The VoiceTable keys                                               |

### Table Voice

|  voice   | type | describe                                                     |
|:--------:|:----:|:-------------------------------------------------------------|
| coquetry | List | The voice that is coquetry                                   |
|  happy   | List | The voice that is happy                                      |                       |
|   sad    | List | The voice that is sad                                        |                       |
|  stable  | List | The voice that is stable (Common)                            |                        |
| welcome  | List | The voice is used to welcome the user when start the program |

## Json File explaining

```json
{
  "settings.compatibility": "录屏兼容 Capture Compatibility",
  "settings.disable": {
    "rec": "Speech Recognition",
    "trans": "Auto Translate",
    "online": "Search Online",
    "media": "Picture/Video Understanding",
    "voice": "AI TTS",
    "gmpene": "Global Mouse Penetration"
  },
  "settings.penetration": {
    "enable": "Weather the penetration is enabled",
    "start": "The time that penetration is disabled"
  }
}
```
