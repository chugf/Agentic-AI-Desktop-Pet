from PyQt5.Qt import Qt, QKeyEvent
from qfluentwidgets import TextEdit, InfoBar, InfoBarPosition, MessageBox


class CodeEdit(TextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
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
        else:
            super().keyPressEvent(event)


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
