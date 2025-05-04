from urllib.parse import quote
import tempfile
from zipfile import ZipFile
import os
import shutil
import glob

from .customize import widgets

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt, QThread, pyqtSignal, QUrl, QIcon, QObject, QRect
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtGui import QPixmap
from qfluentwidgets import FluentIcon, ScrollArea, ExpandLayout, SettingCardGroup, PrimaryPushSettingCard, ProgressBar, \
    BodyLabel


class Fill(QThread):
    dict_signal = pyqtSignal(dict)

    def __init__(self, parent, runtime):
        super().__init__(parent)
        self.runtime = runtime

    def run(self):
        self.dict_signal.emit(self.runtime.get_shop_model())


class Download(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent, url, runtime, configure, index):
        super().__init__(parent)
        self.url = url
        self.runtime = runtime
        self.configure = configure
        self.index = index
        self.reply = None
        self.manager = QNetworkAccessManager(self)

    def start(self):
        self.parent().cards[self.index].button.setText("下载中……")
        self.parent().cards[self.index].setEnabled(False)
        self.reply = self.manager.get(QNetworkRequest(QUrl(self.url)))
        self.reply.downloadProgress.connect(self.on_download_progress)
        self.reply.finished.connect(self.on_finished)

        widgets.pop_notification("正在下载",
                                 f"{self.url.split('/')[-1].split('.')[0]} 正在下载，请稍等...",
                                 "warning")

    def on_download_progress(self, bytesReceived, bytesTotal):
        self.parent().progress_bar.setMaximum(bytesTotal)
        self.parent().progress_bar.setValue(bytesReceived)

    def on_finished(self):
        def check_if_live2d(path: str):
            exist_v3_over = glob.glob(f"{path}/*.model3.json")
            if exist_v3_over:
                return glob.glob(f"{path}/*.model3.json"), 3
            else:
                return glob.glob(f"{path}/*.model.json"), 2

        if self.reply.error() != QNetworkReply.NoError:
            widgets.pop_notification("下载失败", self.reply.errorString(), "error")
            return

        file_name = self.url.split('/')[-1]
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        extract_folder = os.path.join(os.getcwd(), "resources", "model")

        with open(file_path, 'wb') as f:
            f.write(self.reply.readAll().data())

        with ZipFile(file_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            zip_ref.extractall(extract_folder)

        model_name = file_name.split('.')[0]
        target_folder = os.path.join(extract_folder, model_name)

        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

            top_level_items = set(item.split('/')[0] for item in zip_contents)

            if len(top_level_items) == 1:
                possible_folder_name = list(top_level_items)[0]
                extracted_folder = os.path.join(extract_folder, possible_folder_name)

                if os.path.exists(extracted_folder):
                    if os.path.isdir(extracted_folder):
                        for item in os.listdir(extracted_folder):
                            src = os.path.join(extracted_folder, item)
                            dst = os.path.join(target_folder, item)
                            shutil.move(src, dst)
                        os.rmdir(extracted_folder)
                    else:
                        shutil.move(extracted_folder, target_folder)
                else:
                    for item in zip_contents:
                        src = os.path.join(extract_folder, item)
                        dst_dir = os.path.join(target_folder, os.path.dirname(item))
                        dst = os.path.join(dst_dir, os.path.basename(item))

                        if os.path.exists(src):
                            os.makedirs(dst_dir, exist_ok=True)
                            if os.path.exists(dst):
                                if os.path.isdir(dst):
                                    shutil.rmtree(dst)
                                else:
                                    os.remove(dst)
                            shutil.move(src, dst)
            else:
                for item in zip_contents:
                    src = os.path.join(extract_folder, item)
                    dst_dir = os.path.join(target_folder, os.path.dirname(item))
                    dst = os.path.join(dst_dir, os.path.basename(item))

                    if os.path.exists(src):
                        os.makedirs(dst_dir, exist_ok=True)
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)
                        shutil.move(src, dst)

        self.runtime.file.load_template_model(self.configure, model_name)
        live2d, arch = check_if_live2d(f"./resources/model/{model_name}")
        with open(f"./resources/model/{model_name}/{arch}", "w", encoding="utf-8") as f:
            f.write(f"This is a architecture explanation file\nYour architecture is {arch}")
            f.close()
        self.parent().cards[self.index].button.setText("已拥有")
        widgets.pop_notification("下载完成！", f"{model_name} 下载完成！", "success")
        self.finished.emit(model_name)


class CloudDownload(ScrollArea):
    def __init__(self, languages, configure, runtime_module, add_function: callable, add_interface: callable):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.runtime = runtime_module
        self.add_function = add_function
        self.add_interface = add_interface
        self.setObjectName("CloudDownload")

        self.cards = []

        self.scroll_widgets = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widgets)

        self.progress_bar = ProgressBar(self)
        self.progress_bar.setMinimum(0)

        # 模型下载
        self.model_download_group = SettingCardGroup("模型下载", self.scroll_widgets)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 52, 36, 0)

        self.expand_layout.addWidget(self.model_download_group)
        self.progress_bar.setGeometry(QRect(10, 520, 620, 20))
        BodyLabel("Live2D 部分为网上模型，如有侵权请联系：2953911716@qq.com删除！", self).setGeometry(QRect(10, 500, 620, 20))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.scroll_widgets)
        self.scroll_widgets.setObjectName('1ScrollWidget')

        fill = Fill(self, self.runtime)
        fill.dict_signal.connect(self.fill_information)
        fill.start()

    def fill_information(self, result):
        self.cards = [None] * len(result['icon'])
        for index, icon in enumerate(result['icon']):
            manager = QNetworkAccessManager(self)
            manager.finished.connect(lambda r, i=index, res=result: self.icon_finished(r, i, res))
            manager.get(QNetworkRequest(QUrl(quote(icon).replace("%3A", ":"))))

    def icon_finished(self, reply, index, result):
        if reply.error():
            return
        data = reply.readAll()

        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if pixmap.isNull():
            return

        card = PrimaryPushSettingCard(
            icon=QIcon(pixmap),
            text="已拥有" if result['name'][index] in os.listdir("./resources/model/") else "下载",
            title=result['name'][index],
            content=result['description'][index]
        )
        card.setIconSize(40, 40)
        card.setEnabled(False if result['name'][index] in os.listdir("./resources/model/") else True)
        self.cards[index] = card

        download = Download(self, result['url'][index], self.runtime, self.configure, index)
        download.finished.connect(self.add_function)
        card.clicked.connect(download.start)
        self.model_download_group.addSettingCard(card)
        self.add_interface(self, FluentIcon.CLOUD, "云商店")
