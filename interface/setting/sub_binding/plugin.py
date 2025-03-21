import os

from ..customize import function
from ..customize import widgets, highlight

from PyQt5.Qt import QRect, QFont, QFontDatabase
from PyQt5.QtWidgets import QFrame, QButtonGroup

from qfluentwidgets import PushButton, BodyLabel, LineEdit, ComboBox, RadioButton, FluentIcon


class PluginBinding(QFrame):
    def __init__(self, run_function: callable, languages, configure):
        super().__init__()
        self.run_function = run_function
        self.languages = languages
        self.configure = configure
        self.setObjectName("PluginBinding")

        BodyLabel(self.languages[113], self).setGeometry(QRect(20, 10, 200, 30))
        self.input_plugin_folder = LineEdit(self)
        self.input_plugin_folder.setGeometry(QRect(120, 10, 400, 30))

        self.click_select_folder = PushButton(self.languages[40], self)
        self.click_select_folder.setGeometry(QRect(530, 10, 100, 35))
        self.click_select_folder.clicked.connect(self.fill_plugin_information)

        font_id = QFontDatabase.addApplicationFont("./interface/setting/JetBrainsMono-Bold.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        jetbrains_mono = QFont(font_families[0], 10)
        self.input_codes = widgets.CodeEdit(self)
        self.input_codes.setFont(jetbrains_mono)
        self.input_codes.setLineWrapMode(0)
        self.input_codes.setText(open("./interface/subscribe/examples/example_getattr").read())
        self.input_codes.setPlaceholderText("Emm. The developer is slacking off again")
        self.input_codes.setGeometry(QRect(10, 60, 620, 320))
        self.highlighter = highlight.PythonSyntaxHighlighter(self.input_codes.document())

        self.select_examples = ComboBox(self)
        examples = os.listdir("./interface/subscribe/examples")
        self.select_examples.addItems(examples)
        self.select_examples.setGeometry(QRect(500, 60, 130, 30))
        self.select_examples.setCurrentIndex(1)
        self.select_examples.currentTextChanged.connect(
            lambda: self.input_codes.setText(
                open(f"./interface/subscribe/examples/{examples[self.select_examples.currentIndex()]}").read()))

        self.click_running = PushButton(self.languages[114], self)
        self.click_running.setIcon(FluentIcon.CARE_RIGHT_SOLID)
        self.click_running.setGeometry(QRect(10, 390, 100, 30))
        self.click_running.clicked.connect(self.run)

        self.button_groups = QButtonGroup(self)
        self.single_enhancement = RadioButton(self.languages[152], self)
        self.single_independent = RadioButton(self.languages[153], self)
        self.single_automatic = RadioButton(self.languages[154], self)
        self.single_automatic.setChecked(True)
        self.single_enhancement.setGeometry(QRect(130, 390, 150, 30))
        self.single_independent.setGeometry(QRect(280, 390, 150, 30))
        self.single_automatic.setGeometry(QRect(430, 390, 150, 30))
        self.button_groups.addButton(self.single_enhancement)
        self.button_groups.addButton(self.single_independent)
        self.button_groups.addButton(self.single_automatic)

        self.click_compile = PushButton(self.languages[41], self)
        self.click_compile.setGeometry(QRect(10, 430, 620, 30))

    def change_button_text(self, text):
        self.click_running.setText(text)

    def fill_plugin_information(self):
        folder_path = function.select_folder(self, self.languages[40], self.input_plugin_folder)
        general_entrance = f"{folder_path}/main.py"
        if os.path.isfile(general_entrance):
            self.input_codes.clear()
            self.input_codes.setPlainText(open(general_entrance, "r", encoding="utf-8").read())
        else:
            self.input_plugin_folder.clear()
            widgets.pop_error(self, self.languages[112], self.languages[118])

    def run(self):
        self.run_function(self.input_codes.toPlainText(), self.change_button_text, self.button_groups.checkedId())
