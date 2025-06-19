from typing import Literal

from PyQt5.Qt import QApplication, QPixmap, QIcon, QPainter, QLinearGradient, QColor, QFontMetrics, QTimer
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget, QLabel

class GradientLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, Qt.yellow)
        gradient.setColorAt(0.4, QColor(255, 127, 0))
        gradient.setColorAt(0.6, QColor(255, 127, 0))
        gradient.setColorAt(1, Qt.yellow)

        font_metrics = QFontMetrics(self.font())

        text_width = font_metrics.horizontalAdvance(self.text())
        start_x = self.rect().x() + (self.rect().width() - text_width) // 2 if self.alignment() & Qt.AlignHCenter else self.rect().x()
        y = self.rect().y() + (self.rect().height() - font_metrics.height()) // 2 + font_metrics.ascent()

        stops = gradient.stops()
        total_length = len(self.text())

        for i, char in enumerate(self.text()):
            char_width = font_metrics.horizontalAdvance(char)
            char_rect = QRect(start_x, y - font_metrics.ascent(), char_width, font_metrics.height())

            position = i / total_length

            prev_stop = None
            next_stop = None
            for stop_position, stop_color in stops:
                if position <= stop_position:
                    next_stop = (stop_position, stop_color)
                    break
                prev_stop = (stop_position, stop_color)

            if prev_stop is None:
                painter.setPen(next_stop[1])
            elif next_stop is None:
                painter.setPen(prev_stop[1])
            else:
                t = (position - prev_stop[0]) / (next_stop[0] - prev_stop[0])
                r = int(prev_stop[1].red() * (1 - t) + next_stop[1].red() * t)
                g = int(prev_stop[1].green() * (1 - t) + next_stop[1].green() * t)
                b = int(prev_stop[1].blue() * (1 - t) + next_stop[1].blue() * t)
                color = QColor(r, g, b)
                painter.setPen(color)

            painter.drawText(char_rect, Qt.AlignLeft | Qt.AlignVCenter, char)
            start_x += char_width


class StartUp(QWidget):
    def __init__(self):
        super().__init__()
        self.opacity = 0.05
        self.setWindowTitle("Ai Desktop Pet - StartUp")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(QRect(0, 0, 700, 413))
        self.setStyleSheet("background-color: #4169E1;")

        # 右侧放置图片
        self.right_image = QLabel(self)
        self.right_image.setGeometry(QRect(450, 0, 250, 412))
        pixmap = QPixmap("./resources/static/startup.png")
        scaled_pixmap = pixmap.scaled(250, 412, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.right_image.setPixmap(scaled_pixmap)

        # 图标
        self.icon = QLabel(self)
        self.icon.setGeometry(QRect(20, 0, 120, 120))
        icon_pixmap = QPixmap("logo.ico")
        self.icon.setPixmap(icon_pixmap.scaled(80, 81, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 图标下的标题
        self.title = GradientLabel("Artificial Intelligence", self)
        self.title.setStyleSheet("font-size: 17px; font-weight: bold;")
        self.title.setGeometry(QRect(20, 110, 300, 25))

        self.title_name = GradientLabel("Desktop Pet Ver.π", self)
        self.title_name.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.title_name.setGeometry(QRect(20, 135, 300, 25))

        self.address = QLabel("💡 开源地址：https://github.com/HeavyNotFat/Agentic-AI-Desktop-Pet", self)
        self.address.setStyleSheet("color: white;")
        self.address.setGeometry(QRect(20, 200, 400, 25))

        self.notice = QLabel("⚠️ 如果您被付费购买此程序，请注意您可能遭遇了诈骗", self)
        self.notice.setStyleSheet("color: white")
        self.notice.setGeometry(QRect(20, 220, 400, 25))

        self.links = QLabel("💗 友情链接：", self)
        self.links.setStyleSheet("color: white; font-size: 15px")
        self.links.setGeometry(QRect(20, 240, 400, 25))
        self.link_self = QLabel("官网：https://nekocode.top", self)
        self.link_self.setStyleSheet("color: white;")
        self.link_self.setGeometry(QRect(70, 260, 300, 25))
        self.link_live2d_model = QLabel("Live2D 模型： https://github.com/Eikanya/Live2d-model", self)
        self.link_live2d_model.setStyleSheet("color: white;")
        self.link_live2d_model.setGeometry(QRect(70, 280, 380, 25))
        self.link_kooly = QLabel("Kooly 桌宠：  https://kooly.faistudio.top/", self)
        self.link_kooly.setStyleSheet("color: white;")
        self.link_kooly.setGeometry(QRect(70, 300, 300, 25))

        self.model_explanation = QLabel("素材取自：《ENKOPARA》（猫娘乐园）。\n模型制作：HeavyNotFat", self)
        self.model_explanation.setStyleSheet("color: white; font-size: 12px")
        self.model_explanation.setGeometry(QRect(20, 353, 400, 25))

        self.copyright = QLabel("2025 HeavyNotFat  ©️ ️️All rights reserved.", self)
        self.copyright.setStyleSheet("color: white; font-size: 15px")
        self.copyright.setGeometry(QRect(20, 383, 400, 20))

        # 居中显示
        self.screen_geometry = QApplication.desktop().availableGeometry()
        x = (self.screen_geometry.width() - self.width()) // 2
        y = (self.screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.change_opacity('expand'))
        self.timer.start(15)

    def change_opacity(self, status: Literal['expand', 'shrink']):
        self.setWindowOpacity(self.opacity)
        if status == 'expand':
            if self.opacity < 1:
                self.opacity += 0.05
            else:
                self.timer.stop()
                self.init_core()
        else:
            if self.opacity > 0:
                self.opacity -= 0.05
            else:
                self.deleteLater()
                self.timer.stop()
                self.close()

    def init_core(self):
        import core

        self.timer.timeout.connect(lambda: self.change_opacity('shrink'))
        self.timer.start(20)


if __name__ == "__main__":
    app = QApplication([])
    startup = StartUp()
    startup.show()
    app.exec_()
