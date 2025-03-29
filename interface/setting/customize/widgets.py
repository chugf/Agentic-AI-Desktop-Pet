import keyword
import builtins
import string

from PyQt5.Qt import Qt, QStringListModel
from PyQt5.QtWidgets import QCompleter, QComboBox, QVBoxLayout
from qfluentwidgets import TextEdit, InfoBar, InfoBarPosition, MessageBox


class CodeEdit(TextEdit):
    def __init__(self, interface, parent=None):
        super().__init__(parent)
        self.interface = interface
        self.completer = QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.model = QStringListModel()
        self.completer.setModel(self.model)

        self.combo_completer = QComboBox()
        self.combo_completer.setStyleSheet("QComboBox {font-size: 14px;}")
        self.combo_completer.setEditable(False)
        self.combo_completer.setModel(self.model)
        self.combo_completer.hide()
        self.combo_completer.activated.connect(self.insert_completion)

        layout = QVBoxLayout()
        layout.addWidget(self.combo_completer)
        self.setLayout(layout)

        self.textChanged.connect(self.update_completions)
        self.cursorPositionChanged.connect(self.update_completions)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            if self.combo_completer.isVisible():
                completion = self.combo_completer.currentText()
                self.insert_completion(completion)
                self.combo_completer.hide()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Down:
            if self.combo_completer.isVisible():
                index = self.combo_completer.currentIndex()
                if index < self.combo_completer.count() - 1:
                    self.combo_completer.setCurrentIndex(index + 1)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Up:
            if self.combo_completer.isVisible():
                index = self.combo_completer.currentIndex()
                if index > 0:
                    self.combo_completer.setCurrentIndex(index - 1)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()

            previous_text = block.text()
            indent = len(previous_text) - len(previous_text.lstrip())
            if text.strip().endswith(':'):
                self.insertPlainText("\n" + " " * indent + "    ")
            else:
                self.insertPlainText("\n" + " " * indent)
        elif event.key() == Qt.Key_Escape:
            self.combo_completer.hide()
        else:
            super().keyPressEvent(event)

    @staticmethod
    def get_keywords():
        return keyword.kwlist

    def get_other(self):
        def getter(module, text):
            enum_list = []
            for m in dir(module):
                if 'standards' in text:
                    if m.isidentifier() and m[0] in string.ascii_uppercase:
                        enum_list.append(f"{text}.{m}")
                attr = getattr(module, m)
                if not callable(attr) and m.isidentifier() and m[0] in string.ascii_uppercase:
                    for set_ in dir(attr):
                        if set_.isidentifier() and set_[0] in string.ascii_uppercase:
                            enum_list.append(f"{text}.{m}.{set_}()")
            return enum_list

        builtin_functions = [func for func in dir(builtins) if callable(getattr(builtins, func))]
        customize_functions = ["interface.subscribe"]
        customize_functions.extend(getter(self.interface.subscribe, "interface.subscribe"))

        customize_functions.append("interface.subscribe.views")
        customize_functions.extend(getter(self.interface.subscribe.views, "interface.subscribe.views"))
        customize_functions.append("interface.subscribe.actions")
        customize_functions.extend(getter(self.interface.subscribe.actions, "interface.subscribe.actions"))
        customize_functions.append("interface.subscribe.standards")
        customize_functions.extend(getter(self.interface.subscribe.standards, "interface.subscribe.standards"))
        builtin_functions.extend(customize_functions)
        return builtin_functions

    def update_completions(self):
        cursor = self.textCursor()
        block = cursor.block()
        text = block.text()
        pos = cursor.positionInBlock()

        start = pos - 1
        while start >= 0 and text[start].isalnum():
            start -= 1
        start += 1
        prefix = text[start:pos]

        if len(prefix) < 2:
            self.combo_completer.hide()
            return

        filtered_list = []
        for word in self.get_keywords():
            if word.startswith(prefix):
                filtered_list.append(word)
        for word in self.get_other():
            if word.startswith(prefix):
                filtered_list.append(word)
        self.model.setStringList(filtered_list)

        if not filtered_list:
            self.combo_completer.hide()
            return

        rect = self.cursorRect(cursor)
        rect.setY(rect.y() + 25)
        rect.setHeight(25)
        rect.setWidth(500)
        self.combo_completer.setGeometry(rect)
        self.combo_completer.show()

    def insert_completion(self, completion):
        if isinstance(completion, int):
            completion = self.combo_completer.itemText(completion)
        tc = self.textCursor()
        block = tc.block()
        text = block.text()
        pos = tc.positionInBlock()

        start = pos - 1
        while start >= 0 and text[start].isalnum():
            start -= 1
        start += 1

        tc.setPosition(block.position() + start)
        tc.movePosition(tc.Right, tc.KeepAnchor, pos - start)
        tc.insertText(completion)
        self.setTextCursor(tc)


def pop_message(parent, title: str, content: str, yes_text: str = "OK", no_text: str = "Cancel"):
    w = MessageBox(
        title,
        content,
        parent
    )
    w.yesButton.setText(yes_text)
    w.cancelButton.setText(no_text)

    return w.exec()


def pop_warning(parent, title, content, duration=1200, orient=Qt.Horizontal):
    InfoBar.warning(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_success(parent, title, content, duration=1200):
    InfoBar.success(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_error(parent, title, content, duration=2000, orient=Qt.Horizontal):
    InfoBar.error(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )
