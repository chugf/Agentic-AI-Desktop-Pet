import json
import os
import shutil

from ..customize import function, widgets

from PyQt5.Qt import QRect, QTimer
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import BodyLabel, ComboBox, LineEdit, PrimaryPushButton


with open("./resources/template.json", "r", encoding="utf-8") as f:
    template = json.load(f)
    f.close()


class AnimationBinding(QWidget):
    def __init__(self, languages, configure, param_dict, model_json_path, live2d_custom, **kwargs):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.param_dict = param_dict
        self.kwargs = kwargs
        self.setObjectName("AnimationBinding")

        self.motion_dict = live2d_custom.Live2DParameters(model_json_path).get_motions
        self.expression_lists = live2d_custom.Live2DParameters(model_json_path).get_expressions

        BodyLabel(self.languages[42], self).setGeometry(QRect(10, 52, 100, 30))
        self.select_actions = ComboBox(self)
        self.select_actions.addItems(list(self.configure['model'][self.configure['default']]['action'].keys()))
        self.select_actions.currentTextChanged.connect(self.change_action)
        self.select_actions.setGeometry(QRect(100, 52, 200, 30))

        BodyLabel("min(X)", self).setGeometry(QRect(10, 92, 100, 30))
        self.input_min_y = LineEdit(self)
        self.input_min_y.setGeometry(QRect(10, 122, 80, 30))
        BodyLabel("min(Y)", self).setGeometry(QRect(270, 92, 100, 30))
        self.input_min_x = LineEdit(self)
        self.input_min_x.setGeometry(QRect(270, 122, 80, 30))
        BodyLabel("max(X)", self).setGeometry(QRect(140, 92, 100, 30))
        self.input_max_y = LineEdit(self)
        self.input_max_y.setGeometry(QRect(140, 122, 80, 30))
        BodyLabel("max(Y)", self).setGeometry(QRect(400, 92, 100, 30))
        self.input_max_x = LineEdit(self)
        self.input_max_x.setGeometry(QRect(400, 122, 80, 30))
        for index, attr in enumerate([self.input_min_x, self.input_min_y, self.input_max_x, self.input_max_y]):
            attr.setText(str(configure['record']['position'][index]))

        self.click_auto_record = PrimaryPushButton(self.languages[47], self)
        self.click_auto_record.clicked.connect(self.start_record)
        self.click_auto_record.setGeometry(QRect(500, 112, 100, 30))

        BodyLabel(self.languages[44], self).setGeometry(QRect(10, 172, 100, 30))
        self.select_motion_name = ComboBox(self)
        self.select_motion_name.addItems(
            self.motion_dict[list(self.motion_dict.keys())[0]])
        self.select_motion_name.setGeometry(QRect(260, 172, 300, 30))
        self.select_motion_name.currentTextChanged.connect(self.change_motion_name)
        self.select_motion_name.setToolTip(self.languages[91])
        BodyLabel(self.languages[49], self).setGeometry(QRect(260, 202, 100, 30))
        self.select_motion_group = ComboBox(self)
        self.select_motion_group.addItems(list(self.motion_dict.keys()))
        self.select_motion_group.setCurrentIndex(0)
        self.select_motion_group.currentTextChanged.connect(self.change_motion_group)
        self.select_motion_group.setGeometry(QRect(100, 172, 150, 30))
        self.select_motion_group.setToolTip(self.languages[90])
        BodyLabel(self.languages[48], self).setGeometry(QRect(100, 202, 100, 30))

        BodyLabel(self.languages[51], self).setGeometry(QRect(10, 232, 100, 30))
        self.select_expression_name = ComboBox(self)
        self.select_expression_name.addItems(self.expression_lists)
        self.select_expression_name.setText("")
        self.select_expression_name.setGeometry(QRect(100, 232, 300, 30))
        self.select_expression_name.currentTextChanged.connect(self.change_expression_name)

        BodyLabel(self.languages[156], self).setGeometry(QRect(10, 272, 100, 30))
        self.input_import_audio = LineEdit(self)
        self.input_import_audio.setGeometry(QRect(100, 272, 200, 30))
        self.select_save_folder = ComboBox(self)
        self.select_save_folder.addItems(list(template['voice'].keys()))
        self.select_save_folder.setGeometry(QRect(300, 272, 100, 30))
        self.click_choose_audio = PrimaryPushButton(self.languages[102], self)
        self.click_choose_audio.clicked.connect(
            lambda: function.select_file(self, self.languages[52], self.input_import_audio))
        self.click_choose_audio.setGeometry(QRect(400, 272, 100, 30))
        self.click_import_audio = PrimaryPushButton(self.languages[156], self)
        self.click_import_audio.clicked.connect(self.import_audio)
        self.click_import_audio.setGeometry(QRect(510, 272, 100, 30))

        BodyLabel(self.languages[52], self).setGeometry(QRect(10, 312, 100, 30))
        self.select_audio = ComboBox(self)
        self.select_audio.addItems(list(template['voice'].keys()))
        self.select_audio.setGeometry(QRect(100, 312, 300, 30))
        self.select_audio.currentTextChanged.connect(self.change_play_audio)

        BodyLabel(self.languages[53], self).setGeometry(QRect(10, 342, 100, 30))
        self.select_audio_play = ComboBox(self)
        vl = os.listdir(f"./resources/voice/{self.configure['default']}/{self.select_audio.currentText()}")
        vl.append("random")
        self.select_audio_play.addItems(vl)
        self.select_audio_play.setGeometry(QRect(100, 342, 300, 30))

        self.click_save_animation = PrimaryPushButton(self.languages[50], self)
        self.click_save_animation.clicked.connect(self.save_animation)
        self.click_save_animation.setGeometry(QRect(0, 472, 620, 30))

    def import_audio(self):
        audio_basename = os.path.basename(self.input_import_audio.text())
        try:
            shutil.copyfile(self.input_import_audio.text(), f"./resources/voice/"
                                                            f"{self.configure['default']}/"
                                                            f"{self.select_save_folder.currentText()}/{audio_basename}")
            self.select_audio_play.clear()
            vl = os.listdir(f"./resources/voice/{self.configure['default']}/{self.select_audio.currentText()}")
            vl.append("random")
            self.select_audio_play.addItems(vl)

        except shutil.SameFileError:
            pass
        except FileNotFoundError:
            widgets.pop_error(self, "Error", self.languages[155])

    def save_animation(self):
        self.configure["model"][self.configure['default']]['action'][self.select_actions.currentText()]['position'] = [
            int(self.input_min_x.text()), int(self.input_max_x.text()),
            int(self.input_min_y.text()), int(self.input_max_y.text())]
        self.configure["model"][self.configure['default']]['action'][
            self.select_actions.currentText()]['motion'] = (f"{self.select_motion_group.currentText()}:"
                                                            f"{self.select_motion_name.currentText()}:"
                                                            f"{self.select_motion_name.currentIndex()}")
        self.configure["model"][self.configure['default']]['action'][
            self.select_actions.currentText()]['expression'] = self.select_expression_name.currentText()
        self.configure["model"][self.configure['default']]['action'][
            self.select_actions.currentText()]['play_type'] = self.select_audio_play.currentText()
        self.configure["model"][self.configure['default']]['action'][
            self.select_actions.currentText()]['play'] = self.select_audio.currentText()
        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(self.configure, sf, indent=3, ensure_ascii=False)
            sf.close()

    def change_play_audio(self, text):
        self.select_audio_play.clear()
        vl = os.listdir(f"./resources/voice/{self.configure['default']}/{text}")
        vl.append("random")
        self.select_audio_play.addItems(vl)

    def change_action(self, text):
        temp_config = self.configure['model'][self.configure['default']]['action'][text]
        self.input_min_x.setText(str(temp_config['position'][0]))
        self.input_max_x.setText(str(temp_config['position'][1]))
        self.input_min_y.setText(str(temp_config['position'][2]))
        self.input_max_y.setText(str(temp_config['position'][3]))

        self.select_motion_group.setCurrentText(temp_config['motion'].split(":")[0])
        self.select_motion_name.setCurrentText(temp_config['motion'].split(":")[1])

        self.select_expression_name.setCurrentText(temp_config['expression'])
        self.select_audio_play.setCurrentText(temp_config['play_type'])
        self.select_audio.setCurrentText(temp_config['play'])
        del temp_config

    def change_expression_name(self, text):
        self.kwargs.get("pet_model").SetExpression(text)
        self.select_motion_name.setText("")
        self.select_motion_group.setText("")
        QTimer.singleShot(3000, lambda: self.kwargs.get("pet_model").ResetExpression())

    def change_motion_name(self, text):
        self.kwargs.get("pet_model").StartMotion(self.select_motion_group.currentText(),
                                                 self.motion_dict[self.select_motion_group.currentText()].index(text),
                                                 self.kwargs.get("live2d").MotionPriority.FORCE)

    def change_motion_group(self, text):
        self.select_motion_name.clear()
        self.select_motion_name.addItems(self.motion_dict[text])
        self.kwargs.get("pet_model").StartMotion(text, self.motion_dict[text].index(self.select_motion_name.currentText()),
                                                 self.kwargs.get("live2d").MotionPriority.FORCE)
        self.select_expression_name.setText("")

    def start_record(self):
        if widgets.pop_message(self, self.languages[99], self.languages[100], "OK👌"):
            function.change_configure(True, "record.enable_position", self.configure)
            self.kwargs.get("record")()

    def refresh_position(self, min_x, min_y, max_x, max_y):
        self.input_min_x.setText(str(min_x))
        self.input_max_x.setText(str(max_x))
        self.input_min_y.setText(str(min_y))
        self.input_max_y.setText(str(max_y))
