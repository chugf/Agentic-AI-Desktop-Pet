import keyword
import builtins
import string
import inspect

from PyQt5.Qt import Qt, QStringListModel, QStandardItemModel, QFont, QIcon, QStandardItem, QTimer
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
        self.combo_completer.setFont(QFont("微软雅黑", 11))
        self.combo_completer.setEditable(False)
        self.combo_completer.setModel(self.model)
        self.combo_completer.hide()
        self.combo_completer.activated.connect(self.click_complete)

        layout = QVBoxLayout()
        layout.addWidget(self.combo_completer)
        self.setLayout(layout)

        self.textChanged.connect(self.update_completions)
        self.cursorPositionChanged.connect(self.update_completions)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            if self.combo_completer.isVisible():
                self.insert_completion(self.combo_completer.currentIndex())
                self.combo_completer.hide()
            else:
                self.insertPlainText("    ")
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
        elif event.key() == Qt.Key_Period:
            self.update_completions()
            super().keyPressEvent(event)
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

        packages = ["views", "actions", "standards"]
        customize_functions = ["interface", "interface.subscribe"]
        customize_functions.extend(getter(self.interface.subscribe, "interface.subscribe"))
        for package in packages:
            customize_functions.append(f"interface.subscribe.{package}")
            customize_functions.extend(getter(self.interface.subscribe.views, f"interface.subscribe.{package}"))

        builtin_functions.extend(customize_functions)
        return builtin_functions

    def update_completions(self):
        def get_completions(module_, parts_, current_prefix):
            if not parts_:
                return

            first_part = parts_[0]
            remaining_parts = parts_[1:]

            for m in dir(module_):
                if m[0] == "_":
                    continue
                if m.startswith(first_part):
                    attr = getattr(module_, m, None)
                    if not remaining_parts:
                        if inspect.ismodule(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "module", m))
                        elif inspect.isclass(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "class", m))
                        elif callable(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "function", m))
                        else:
                            filtered_list.append((f"{current_prefix}.{m}", "variable", m))
                    else:
                        if attr:
                            get_completions(attr, remaining_parts, f"{current_prefix}.{m}")

        cursor = self.textCursor()
        block = cursor.block()
        text = block.text()
        pos = cursor.positionInBlock()

        start = pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == '.'):
            start -= 1
        start += 1
        prefix = text[start:pos]

        if len(prefix) < 2:
            self.combo_completer.hide()
            return

        parts = prefix.split('.')
        filtered_list = []

        if len(parts) == 1:
            for word in self.get_keywords():
                if word.startswith(prefix):
                    filtered_list.append((word, "keyword", word))
            for word in self.get_other():
                if word.startswith(prefix):
                    filtered_list.append((word, "variable", word))
        else:
            module_name = parts[0]
            if module_name == "interface":
                module = self.interface
            elif module_name == "builtins":
                module = builtins
            else:
                module = None

            if module:
                get_completions(module, parts[1:], module_name)

        item_model = QStandardItemModel()
        for full_path, item_type, display_text in filtered_list:
            icon = QIcon(f"./resources/static/{item_type}.png")
            q_item = QStandardItem(icon, display_text)
            q_item.setData(full_path, Qt.UserRole)
            item_model.appendRow(q_item)

        self.combo_completer.setModel(item_model)

        if not filtered_list:
            self.combo_completer.hide()
            return

        rect = self.cursorRect(cursor)
        rect.setX(0)
        rect.setY(rect.y() + 25)
        rect.setHeight(25)
        rect.setWidth(500)
        self.combo_completer.setGeometry(rect)
        self.combo_completer.show()

    def click_complete(self, completion):
        self.insert_completion(completion)
        QTimer.singleShot(50, self.setFocus)

    def insert_completion(self, completion):
        if isinstance(completion, int):
            completion = self.combo_completer.itemData(completion, Qt.UserRole)
        tc = self.textCursor()
        block = tc.block()
        text = block.text()
        pos = tc.positionInBlock()

        start = pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == '.'):
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


def pop_success(parent, title, content, duration=1200, orient=Qt.Horizontal):
    InfoBar.success(
        title=title,
        content=content,
        orient=orient,
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
