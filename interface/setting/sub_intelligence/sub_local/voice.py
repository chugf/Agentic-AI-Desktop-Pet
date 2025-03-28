from ...customize import function, constants

from PyQt5.Qt import Qt, QRect
from PyQt5.QtWidgets import QWidget

from qfluentwidgets import BodyLabel, Slider


class VoiceParameter(QWidget):
    def __init__(self, configure, parent=None):
        super().__init__(parent)
        self.configure = configure
        self.setObjectName("VoiceParameter")

        # top_k
        BodyLabel("top_k", self).setGeometry(QRect(10, 42, 60, 35))
        self.show_top_k = BodyLabel(top_k := str(configure['settings']['tts']['top_k']), self)
        self.top_k = Slider(Qt.Horizontal, self)
        self.top_k.setRange(1, 100)
        self.top_k.setGeometry(QRect(100, 52, 300, 35))
        self.top_k.setValue(int(configure['settings']['tts']['top_k']))
        self.top_k.setToolTip(top_k)
        self.top_k.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.top_k", self.top_k, self.show_top_k))
        self.show_top_k.setGeometry(QRect(420, 42, 60, 35))

        # top_p
        BodyLabel("top_p", self).setGeometry(QRect(10, 77, 60, 35))
        self.show_top_p = BodyLabel(top_p := str(configure['settings']['tts']['top_p']), self)
        self.top_p = Slider(Qt.Horizontal, self)
        self.top_p.setRange(1, constants.TOP_P_PRECISION)
        self.top_p.setGeometry(QRect(100, 87, 300, 35))
        self.top_p.setValue(int(configure['settings']['tts']['top_p'] * constants.TOP_P_PRECISION))
        self.top_p.setToolTip(top_p)
        self.top_p.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.top_p", self.top_p, self.show_top_p, constants.TOP_P_PRECISION))
        self.show_top_p.setGeometry(QRect(420, 87, 60, 35))

        # temperature
        BodyLabel("temperature", self).setGeometry(QRect(10, 117, 80, 35))
        self.show_temperature = BodyLabel(temperature := str(configure['settings']['tts']['temperature']), self)
        self.temperature = Slider(Qt.Horizontal, self)
        self.temperature.setRange(1, constants.TEMPERATURE_PRECISION)
        self.temperature.setGeometry(QRect(100, 127, 300, 35))
        self.temperature.setValue(int(configure['settings']['tts']['temperature'] * constants.TEMPERATURE_PRECISION))
        self.temperature.setToolTip(temperature)
        self.temperature.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.temperature",
                self.temperature, self.show_temperature, constants.TEMPERATURE_PRECISION))
        self.show_temperature.setGeometry(QRect(420, 117, 60, 35))

        # speed
        BodyLabel("speed", self).setGeometry(QRect(10, 152, 60, 35))
        self.show_speed = BodyLabel(speed := str(configure['settings']['tts']['speed']), self)
        self.speed = Slider(Qt.Horizontal, self)
        self.speed.setRange(1, 2 * constants.SPEED_PRECISION)
        self.speed.setGeometry(QRect(100, 162, 300, 35))
        self.speed.setValue(int(configure['settings']['tts']['speed'] * constants.SPEED_PRECISION))
        self.speed.setToolTip(speed)
        self.speed.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.speed", self.speed, self.show_speed, constants.SPEED_PRECISION))
        self.show_speed.setGeometry(QRect(420, 152, 60, 35))

        # batch_size
        BodyLabel("batch_size", self).setGeometry(QRect(10, 197, 80, 35))
        self.show_batch_size = BodyLabel(batch_size := str(configure['settings']['tts']['batch_size']), self)
        self.batch_size = Slider(Qt.Horizontal, self)
        self.batch_size.setRange(1, 100)
        self.batch_size.setGeometry(QRect(100, 207, 300, 35))
        self.batch_size.setValue(int(configure['settings']['tts']['batch_size']))
        self.batch_size.setToolTip(batch_size)
        self.batch_size.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.batch_size", self.batch_size, self.show_batch_size))
        self.show_batch_size.setGeometry(QRect(420, 197, 60, 35))

        # batch_threshold
        BodyLabel("batch_threshold", self).setGeometry(QRect(10, 232, 100, 35))
        self.show_batch_threshold = BodyLabel(
            batch_threshold := str(configure['settings']['tts']['batch_threshold']), self)
        self.batch_threshold = Slider(Qt.Horizontal, self)
        self.batch_threshold.setRange(1, 100)
        self.batch_threshold.setGeometry(QRect(100, 242, 300, 35))
        self.batch_threshold.setValue(
            int(configure['settings']['tts']['batch_threshold'] * constants.BATCH_THRESHOLD_PRECISION))
        self.batch_threshold.setToolTip(batch_threshold)
        self.batch_threshold.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.tts.batch_threshold",
                self.batch_threshold, self.show_batch_threshold, constants.BATCH_THRESHOLD_PRECISION))
        self.show_batch_threshold.setGeometry(QRect(420, 232, 60, 35))

    def value_changed(self, value, relative, slider_widget, label_widget, precision=1):
        # 判断是否是整数
        if value / precision % 1 == 0:
            result = int(value / precision)
        else:
            result = float(value / precision)

        label_widget.setText(str(result))
        slider_widget.setToolTip(str(result))
        function.change_configure(result, relative, self.configure)
        
        