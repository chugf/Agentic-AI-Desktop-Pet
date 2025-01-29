<div align="center">
    <h1 style="margin: 0;">人工知能デスクトップペット</h1>
    <b><a href="README.md">English</a></b>
    <b> | </b>
    <b><a href="README_zh.md">简体中文</a></b>
    <b> | </b>
    <b><a href="README_ja.md">日本語</a></b>
</div>

# 紹介

これはユーザーと対話するために人工知能を利用したデスクトップペットです。

> 開発者：**少し*退屈*かもしれない...**？

# 利点

**他のデスクトップペットとは異なる点がいくつかあります。**

### 人工知能

- 人工知能インタラクション

> テキストや音声で対話を楽しむことができます。

- 人工知能エージェント

> AIは開発者が書いた関数を利用してコンピュータを操作することができます。
>
> AIはユーザーが何をしているかを見るためにスクリーンキャプチャも可能です。

### リソースローダー

- Live2Dモデル

> 最高の体験を得るためにLive2Dエンジンを使用して表示およびモデルを作成します。

### セーフティとカスタマイズ

- カスタマイズ

> モデル、効果、音声、AI推論方法をカスタマイズすることができ、さらにはAIモデル自体も置き換えることが可能です。

# モデルの置き換え

## 手順

**以下の手順に従ってモデルを置き換えることが可能です：**

1. *ダウンロード*お好みのモデル。
2. *編集* jsonファイルを例（Vanilla.json）に従って編集します。
3. *右クリック* 元のモデルを選択し、「キャラクター変更」->「自分のモデルを選択」を選択します。
4. *リロード* プログラムを再読み込みします。

## Jsonファイルフォーマット

基本

```textmate
name        :         $ .string （表示名および音声呼び出し名）
voice_model :         $ .string （音声モデル名 (GSV)）
default     :         $ .string （プログラム開始時に最初に読み込むモデル）
```

高度な設定

|             オブジェクト              |             値*              | タイプ  | 使用目的                           |
|:-------------------------------:|:---------------------------:|:----:|--------------------------------|
|    model.\<YourModel>.adult     |        AdultContent         | dict | 成人向けコンテンツがサポートされているかどうかを判断します。 |
|    model.\<YourModel>.adult     |      AdultLevelMinimum      | dict | 成人向けレベルの最小値                    |
|    model.\<YourModel>.adult     |      AdultLevelMaximum      | dict | 成人向けレベルの最大値                    |
|    model.\<YourModel>.adult     |        AdultDescribe        | dict | 成人向けの説明                        |
| model.\<YourModel>.adult.action | Action\<DescribeEnglish>[1] | list | 使用可能な成人向けアクション                 |
| model.\<YourModel>.adult.voice  | Voice\<DescribeEnglish>[2]  | list | 再生したい成人向け音声                    |
|    model.\<YourModel>.action    |        [TableAction]        | dict | 使用可能な一般的なアクション                 |
|    model.\<YourModel>.voice     |        [TableVoice]         | dict | 再生したい一般的な音声                    |

1. AdultDescribe English （説明は英語で記述する必要があります）
2. AdultDescribe English （説明は英語で記述する必要があります）

### テーブル アクション

|      アクション      |  パラメータ  |   タイプ   | 説明                                  |
|:---------------:|:-------:|:-------:|:------------------------------------|
| ActionTouchHead |  param  | String  | Live2Dパラメータ呼び出し                     |
| ActionTouchHead | reverse | Boolean | ステッチアニメーションを逆順で実行する必要があるかどうかチェックします |
| ActionTouchHead |  play   | String  | VoiceTableキー                        |

### テーブル 音声

|    音声    | タイプ  | 説明                          |
|:--------:|:----:|:----------------------------|
| coquetry | List | 愛らしさの声                      |
|  happy   | List | 喜びの声                        |
|   sad    | List | 悲しみの声                       |
|  stable  | List | 安定した声（一般的）                  |
| welcome  | List | プログラム開始時にユーザーを歓迎するために使用される声 |

## Jsonファイルの説明

```json
{
  "settings.compatibility": "画面録画互換性 Capture Compatibility",
  "settings.disable": {
    "rec": "音声認識 Speech Recognition",
    "trans": "自動翻訳 Auto Translate",
    "online": "オンライン検索 Search Online",
    "media": "画像/ビデオ理解 Picture/Video Understanding",
    "voice": "AI TTS",
    "gmpene": "グローバルマウス透過 Global Mouse Penetration"
  },
  "settings.penetration": {
    "enable": "透過が有効かどうか",
    "start": "透過が無効になる時間"
  }
}
```

