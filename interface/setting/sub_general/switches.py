import subprocess
import os

from ..customize import function, constants

from PyQt5.Qt import Qt, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from qfluentwidgets import SettingCardGroup, SwitchSettingCard, OptionsSettingCard, \
    OptionsConfigItem, BoolValidator, QConfig, qconfig, OptionsValidator, ExpandLayout, ComboBoxSettingCard, \
    FluentIcon, ScrollArea, InfoBar, InfoBarPosition, ExpandGroupSettingCard, BodyLabel, SwitchButton, IndicatorPosition, \
    ComboBox

env = os.environ.copy()
python_path = subprocess.check_output(["where", "python"], env=env).decode().replace(
    "\r", "").split("\n")

class Config(QConfig):
    compatible = OptionsConfigItem("General", "compatible", False, BoolValidator())
    adult = OptionsConfigItem("General", "adult", False, BoolValidator())
    recognition = OptionsConfigItem("General", "recognition", False, BoolValidator())
    speaker = OptionsConfigItem("General", "speaker", False, BoolValidator())
    search = OptionsConfigItem("General", "search", False, BoolValidator())

    penetration = OptionsConfigItem(
        "Advanced", "penetration", "shut",
        OptionsValidator(["shut", "next", "left-bottom", "left-top", "right-bottom", "right-top"]), restart=True)
    taskbar_lock = OptionsConfigItem("Advanced", "locktsk", True, BoolValidator())
    media_understanding = OptionsConfigItem("Advanced", "media", False, BoolValidator())
    safety_examine = OptionsConfigItem(
        "Advanced", "safety", "shut",
        OptionsValidator(["shut", "l1", "l2", "l3", "l4", "l5"]), restart=True)
    audio_visualization = OptionsConfigItem("Advanced", "visualization", False, BoolValidator())
    realtime_api = OptionsConfigItem("Advanced", "realtime", False, BoolValidator())
    local_python_path = OptionsConfigItem(
        "Advanced", "python", python_path[0], OptionsValidator(python_path), restart=True)

    live2d_blink = OptionsConfigItem("Live2D", "AutoBlink", True, BoolValidator())
    live2d_breath = OptionsConfigItem("Live2D", "AutoBreath", True, BoolValidator())
    live2d_drag = OptionsConfigItem("Live2D", "AutoDrag", True, BoolValidator())

    physics_switch = OptionsConfigItem("Physics", "physics", True, BoolValidator())
    physics_bounce = OptionsConfigItem("Physics", "bounce", True, BoolValidator())
    physics_dumping_motion = OptionsConfigItem("Physics", "dumping", True, BoolValidator())


class TranslateCard(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(FluentIcon.LANGUAGE, parent.languages[16], parent.languages[93], parent)
        self.parent = parent
        self.enable_label = BodyLabel(parent.languages[233], self)
        self.enable_switch_button = SwitchButton("关", self, IndicatorPosition.RIGHT)
        self.enable_switch_button.setChecked(parent.configure['settings']['enable']['trans'])
        self.enable_switch_button.setOnText("开")
        self.enable_switch_button.setFixedWidth(135)
        self.enable_switch_button.checkedChanged.connect(
            lambda value: function.change_configure(
                value, "settings.enable.trans", parent.configure
            ))
        self.add(self.enable_label, self.enable_switch_button)

        self.target_label = BodyLabel(parent.languages[234], self)
        self.target_combo_box = ComboBox(self)
        self.target_combo_box.addItems([
            parent.languages[235],
            parent.languages[236],
            parent.languages[237],
            parent.languages[238],
        ])
        if parent.configure['settings']['trans_lang'] == "zh-Hans":
            self.target_combo_box.setCurrentText(parent.languages[235])
        elif parent.configure['settings']['trans_lang'] == "en":
            self.target_combo_box.setCurrentText(parent.languages[236])
        elif parent.configure['settings']['trans_lang'] == "ja":
            self.target_combo_box.setCurrentText(parent.languages[237])
        elif parent.configure['settings']['trans_lang'] == "ko":
            self.target_combo_box.setCurrentText(parent.languages[238])
        self.target_combo_box.currentTextChanged.connect(self.change_language)
        self.target_combo_box.setFixedWidth(200)
        self.add(self.target_label, self.target_combo_box)

    def change_language(self, text):
        if text == self.parent.languages[235]:
            function.change_configure(
                "zh-Hans", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[236]:
            function.change_configure(
                "en", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[237]:
            function.change_configure(
                "ja", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[238]:
            function.change_configure(
                "ko", "settings.trans_lang", self.parent.configure
            )

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)


class Switches(ScrollArea):
    def __init__(self, languages, cache_config, configure):
        super().__init__()
        self.setObjectName("SwitchesG")
        self.cache_config = cache_config
        self.languages = languages
        self.configure = configure

        self.scroll_widgets = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widgets)
        qconfig.load("./interface/setting/sub_general/switch.json", Config)
        # 常规设置
        self.general_group = SettingCardGroup(self.languages[11], self.scroll_widgets)
        self.card_compatible_capture = SwitchSettingCard(
            icon=FluentIcon.FIT_PAGE,
            title=self.languages[12],
            content=self.languages[85],
            parent=self.general_group,
            configItem=Config.compatible,
        )
        self.card_compatible_capture.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.compatibility",
                value, "General.compatible"
            ))
        self.general_group.addSettingCard(self.card_compatible_capture)
        self.card_adult = SwitchSettingCard(
            configItem=Config.adult,
            icon=FluentIcon.HEART,
            title=self.languages[5],
            content=self.languages[87],
            parent=self.general_group
        )
        self.card_adult.checkedChanged.connect(
            lambda value: self.pop_success(
                self.languages[88], self.languages[89],
                function.change_configure, 1 if value else 0, "adult_level", self.configure))
        self.general_group.addSettingCard(self.card_adult)
        self.card_recognition = SwitchSettingCard(
            configItem=Config.recognition,
            icon=FluentIcon.MICROPHONE,
            title=self.languages[13],
            content=self.languages[90],
            parent=self.general_group
        )
        self.card_recognition.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.rec",
                value, "General.recognition"
            ))
        self.general_group.addSettingCard(self.card_recognition)
        self.card_speaker = SwitchSettingCard(
            configItem=Config.speaker,
            icon=FluentIcon.SPEAKERS,
            title=self.languages[14],
            content=self.languages[91],
            parent=self.general_group
        )
        self.card_speaker.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.tts",
                value, "General.speaker"
            ))
        self.general_group.addSettingCard(self.card_speaker)
        self.card_search = SwitchSettingCard(
            configItem=Config.search,
            icon=FluentIcon.SEARCH,
            title=self.languages[15],
            content=self.languages[92],
            parent=self.general_group
        )
        self.card_search.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.online",
                value, "General.search"
            ))
        self.general_group.addSettingCard(self.card_search)
        self.card_translate = TranslateCard(
            self
        )
        # self.card_translate = SwitchSettingCard(
        #     configItem=Config.translate,
        #     icon=FluentIcon.LANGUAGE,
        #     title=self.languages[16],
        #     content=self.languages[93],
        #     parent=self.general_group
        # )
        # self.card_translate.checkedChanged.connect(
        #     lambda value: self.change_configure(
        #         value, "settings.enable.trans",
        #         value, "General.translate"
        #     ))
        self.general_group.addSettingCard(self.card_translate)

        # 高级设置
        self.advanced_group = SettingCardGroup(self.languages[17], self.scroll_widgets)
        self.media_understanding = SwitchSettingCard(
            configItem=Config.media_understanding,
            icon=FluentIcon.PHOTO,
            title=self.languages[18],
            content=self.languages[86],
            parent=self.advanced_group
        )
        self.media_understanding.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.media",
                value, "Advanced.media"
            ))
        self.advanced_group.addSettingCard(self.media_understanding)
        self.card_mouse_penetration = OptionsSettingCard(
            Config.penetration,
            icon=FluentIcon.TRANSPARENT,
            title=self.languages[19],
            content=self.languages[59],
            texts=[self.languages[20], self.languages[21], self.languages[22],
                   self.languages[23], self.languages[24], self.languages[25]],
            parent=self.advanced_group
        )
        self.card_mouse_penetration.optionChanged.connect(
            lambda value: function.change_configure(
                value.value, "Advanced.penetration", cache_config, constants.CACHE_CONFIGURE_PATH))
        self.advanced_group.addSettingCard(self.card_mouse_penetration)
        self.card_realtime_api = SwitchSettingCard(
            configItem=Config.realtime_api,
            icon=QIcon("./resources/static/realtime.png"),
            title=self.languages[198],
            content=self.languages[199],
            parent=self.advanced_group
        )
        self.card_realtime_api.setIconSize(18, 18)
        self.card_realtime_api.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.realtimeAPI",
                value, "Advanced.realtime"
            ))
        self.advanced_group.addSettingCard(self.card_realtime_api)

        self.card_taskbar_lock = SwitchSettingCard(
            configItem=Config.taskbar_lock,
            icon=FluentIcon.PIN,
            title=self.languages[26],
            content=self.languages[60],
            parent=self.advanced_group
        )
        self.card_taskbar_lock.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.locktsk",
                value, "Advanced.locktsk"
            ))
        self.advanced_group.addSettingCard(self.card_taskbar_lock)

        self.card_safety_examine = OptionsSettingCard(
            configItem=Config.safety_examine,
            icon=FluentIcon.VPN,
            title=self.languages[126],
            content=self.languages[125],
            texts=[self.languages[20], self.languages[120], self.languages[121],
                   self.languages[122], self.languages[123], self.languages[124]],
            parent=self.advanced_group
        )
        self.card_audio_visualization = SwitchSettingCard(
            configItem=Config.audio_visualization,
            icon=FluentIcon.MUSIC,
            title=self.languages[138],
            content=self.languages[139],
            parent=self.advanced_group
        )
        self.card_audio_visualization.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.visualization",
                value, "Advanced.visualization"
            ))
        self.advanced_group.addSettingCard(self.card_audio_visualization)
        self.card_safety_examine.optionChanged.connect(
            lambda value: self.change_configure(
                value.value, "settings.safety",
                value.value, "Advanced.safety"
            ))
        self.advanced_group.addSettingCard(self.card_safety_examine)
        self.local_python_path_card = ComboBoxSettingCard(
            configItem=Config.local_python_path,
            icon=FluentIcon.CODE,
            title=self.languages[214],
            content=self.languages[215],
            parent=self.advanced_group,
            texts=python_path
        )
        Config.local_python_path.valueChanged.connect(
            lambda value: self.change_configure(
                value, "settings.python",
                value, "Advanced.python"
            ))
        self.advanced_group.addSettingCard(self.local_python_path_card)

        # Live2D 设置
        self.live2d_group = SettingCardGroup(f"Live2D {self.languages[10]}", self.scroll_widgets)
        self.card_auto_blink = SwitchSettingCard(
            configItem=Config.live2d_blink,
            icon=FluentIcon.VIEW,
            title=self.languages[53],
            content=self.languages[53],
            parent=self.live2d_group
        )
        self.card_auto_blink.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoBlink",
                value, "Live2D.AutoBlink"
            ))
        self.live2d_group.addSettingCard(self.card_auto_blink)
        self.card_auto_breath = SwitchSettingCard(
            configItem=Config.live2d_breath,
            icon=FluentIcon.SYNC,
            title=self.languages[54],
            content=self.languages[54],
            parent=self.live2d_group
        )
        self.card_auto_breath.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoBreath",
                value, "Live2D.AutoBreath"
            ))
        self.live2d_group.addSettingCard(self.card_auto_breath)
        self.card_auto_drag = SwitchSettingCard(
            configItem=Config.live2d_drag,
            icon=FluentIcon.MOVE,
            title=self.languages[55],
            content=self.languages[55],
            parent=self.live2d_group
        )
        self.card_auto_drag.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoDrag",
                value, "Live2D.AutoDrag"
            ))
        self.live2d_group.addSettingCard(self.card_auto_drag)

        # 物理模拟
        self.physics_group = SettingCardGroup(self.languages[183], self.scroll_widgets)
        self.total_switch = SwitchSettingCard(
            configItem=Config.physics_switch,
            icon=QIcon("./resources/static/physics.png"),
            title=self.languages[184],
            content=self.languages[185],
            parent=self.physics_group
        )
        self.total_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.total",
                value, "Physics.switch"
            ))
        self.total_switch.setIconSize(20, 20)
        self.physics_group.addSettingCard(self.total_switch)
        self.bounce_switch = SwitchSettingCard(
            configItem=Config.physics_bounce,
            icon=QIcon("./resources/static/bounce.png"),
            title=self.languages[186],
            content=self.languages[187],
            parent=self.physics_group
        )
        self.bounce_switch.setIconSize(20, 20)
        self.bounce_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.bounce",
                value, "Physics.bounce"
            ))
        self.physics_group.addSettingCard(self.bounce_switch)
        self.dumping_motion_switch = SwitchSettingCard(
            configItem=Config.physics_dumping_motion,
            icon=QIcon("./resources/static/dumping.png"),
            title=self.languages[188],
            content=self.languages[189],
            parent=self.physics_group
        )
        self.dumping_motion_switch.setIconSize(20, 20)
        self.dumping_motion_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.dumping",
                value, "Physics.dumping"
            ))
        self.physics_group.addSettingCard(self.dumping_motion_switch)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 52, 36, 0)
        self.expand_layout.addWidget(self.general_group)
        self.expand_layout.addWidget(self.advanced_group)
        self.expand_layout.addWidget(self.live2d_group)
        self.expand_layout.addWidget(self.physics_group)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.scroll_widgets)
        self.scroll_widgets.setObjectName('ScrollWidget')

    def change_configure(self, value, relative, cache_value, cache_relative):
        print(value, relative)
        function.change_configure(cache_value, cache_relative, self.cache_config, constants.CACHE_CONFIGURE_PATH)
        function.change_configure(value, relative, self.configure)

    def pop_success(self, title, content, func, *args):
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1200,
            parent=self
        )
        func(*args)


Config = Config()
