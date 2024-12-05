from io import BytesIO
import os
import sys
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont, QShortcut, QKeySequence, QPalette
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
import requests
from game import GetDaiLyGames
from searchBar import *
import barRaceCharts.BarChartDataConvert as BCconvert
import playersCharts.getPlayers_GameChart as PCconvert
import PriceChart.generate_all_charts as DFConvert

import ctypes

myappid = "mycompany.myproduct.subproduct.version"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QApplication(sys.argv)
app_icon = QIcon()
app_icon.addFile("image/icon.png", QSize(256, 256))

app.setWindowIcon(app_icon)
app.setStyle("fusion")

palette = app.palette()
is_dark_mode = palette.color(QPalette.ColorRole.Window).value() < 128

font_id = QFontDatabase.addApplicationFont("FVF_Fernando_08.ttf")
font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
pixelfont = QFont(font_family, 20)


def fixed_pixelfont(item, size: int):
    pixelfont.setPointSize(size)

    if not isinstance(item, list):
        item = [item]
    for i in item:
        i.setFont(pixelfont)


verticalScrollBarStyle = """ QScrollBar:vertical {
                border: none;
                width: 12px;
                background:black;
                margin: 15px 0 15px 0;
                border-radius: 0px;
            }

            /*  HANDLE BAR VERTICAL */
            QScrollBar::handle:vertical {
                background-color: white;
                min-height: 30px;
                border-radius: 7px;
                border:3px solid black;
            }
            QScrollBar::handle:vertical:hover{
                background-color:silver;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: rgb(185, 0, 92);
            }

            /* BTN TOP - SCROLLBAR */
            QScrollBar::sub-line:vertical {
                border:3px solid black;
                background-color: white;
                height: 15px;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical:hover {
                background-color: silver;
            }
            QScrollBar::sub-line:vertical:pressed {
                background-color: rgb(185, 0, 92);
            }

            /* BTN BOTTOM - SCROLLBAR */
            QScrollBar::add-line:vertical {
                border:3px solid black;
                background-color: white;
                height: 15px;
                border-bottom-left-radius: 7px;
                border-bottom-right-radius: 7px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical:hover {
                background-color: silver;
            }
            QScrollBar::add-line:vertical:pressed {
                background-color: rgb(185, 0, 92);
            }

            /* RESET ARROW */
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            """


def get_pixmap_from_url(url):
    try:
        if url:
            response = requests.get(url)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data.getvalue()):
                return pixmap
        fallback_path = os.path.join(os.path.dirname(__file__), "image/steam.jpg")
        return QPixmap(fallback_path)
    except Exception as e:
        print(f"Lỗi khi tải ảnh từ {url}: {e}")
        fallback_path = os.path.join(os.path.dirname(__file__), "image/steam.jpg")
        return QPixmap(fallback_path)


class ChartFullScreen(QMainWindow):
    def __init__(self, url):

        super(ChartFullScreen, self).__init__()
        self.web_view = QWebEngineView(self)
        self.web_view.load(QUrl(url))
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.web_view)
        self.setCentralWidget(widget)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        shortcut = QShortcut(QKeySequence("Esc"), self)
        shortcut.activated.connect(self.close)


class ChartStage(QMainWindow):
    def __init__(self, type: str, parent):
        self.type = type
        super(ChartStage, self).__init__()
        self.setWindowTitle(type + " charts")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        uic.loadUi("test3.ui", self)

        self.loading_screen = LoadingScreen(self).text
        self.loading_screen.show()

        if type != "steamUsers":
            self.loader_thread = chartLoaderThread(type)
            self.loader_thread.data_loaded.connect(self.display)
            self.loader_thread.start()
        else:
            self.display()

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        parent_geometry = parent.geometry()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()

        self.setGeometry(parent_x, parent_y, parent_width, parent_height)

    def display(self):
        self.web_view = QWebEngineView(self)

        if self.type == "steamUsers":
            self.web_view.load(QUrl("http://127.0.0.1:5500/mapWorld/index.html"))
            self.chartName.setText("Charts showing the world map of Steam Users")

        else:
            self.web_view.load(
                QUrl("http://127.0.0.1:5500/barRaceCharts/BarRace_all.html")
            )
            chartStr = self.type + " games"
            self.chartName.setText(
                "Bar chart showing the monthly ranking of "
                + chartStr
                + " from November 2021 to November 2024"
            )

        fixed_pixelfont(self.chartName, 15)
        self.backButton.setText("Back")
        self.backButton.clicked.connect(self.close)
        self.backButton.setStyleSheet(
            """
                QPushButton {
                    border:3px solid black;
                    border-radius:5px;
                    padding-bottom: 5px;

                }
                QPushButton:hover {
                    background-color: lightgray;
                    border:4px solid black;

                }
            """
        )
        fixed_pixelfont(self.backButton, 8)

        container = self.findChild(QWidget, "ChartsWidget")
        layout = QVBoxLayout(container)
        container.setLayout(layout)
        container.setStyleSheet(
            """
            QWidget {
                border: 3px solid black;

            }
        """
        )
        layout.addWidget(self.web_view)
        self.loading_screen.hide()


class gameStage(QMainWindow):
    def __init__(self, item, pixmap: QPixmap, parent):
        super(gameStage, self).__init__()
        self.item = item
        self.pixmap = pixmap

        self.setWindowTitle(item.title + " info")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        uic.loadUi("test2.ui", self)

        fixed_pixelfont(self.gameName, 26)
        fixed_pixelfont(self.label, 18)
        fixed_pixelfont(self.gameScore, 14)
        fixed_pixelfont(self.label_10, 14)
        fixed_pixelfont([self.label_4, self.label_5, self.label_7, self.label_9], 10)

        fixed_pixelfont(
            [
                self.steamScore,
                self.steamCount,
                self.metaScore,
                self.metaCount,
                self.metaUserScore,
                self.metaUserCount,
                self.openCriticScore,
                self.openCriticScore,
                self.openCriticCount,
                self.recentPlayerCount,
                self.dayPlayerCount,
                self.weekPlayerCount,
                self.peak,
                self.label_11,
            ],
            20,
        )
        pixelfont.setPointSize(14)
        pixelfont.setBold(True)
        self.label_12.setFont(pixelfont)
        pixelfont.setBold(False)

        self.releaseDate.setFont(pixelfont)
        self.tags.setFont(pixelfont)
        self.rank.setFont(pixelfont)
        pixelfont.setPointSize(22)
        self.latestPrice.setFont(pixelfont)
        self.basePrice.setFont(pixelfont)
        pixelfont.setPointSize(48)
        self.sale.setFont(pixelfont)
        pixelfont.setPointSize(8)
        self.closeButton.setFont(pixelfont)
        self.closeButton.setText("Back")

        self.loading_screen = LoadingScreen(self).text
        self.loading_screen.show()

        self.loader_thread = gameDataLoaderThread(item)
        self.loader_thread.data_loaded.connect(self.display)
        self.loader_thread.data_unloaded.connect(self.close)
        self.loader_thread.start()

        parent_geometry = parent.geometry()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()

        self.setGeometry(parent_x, parent_y, parent_width, parent_height)

    def display(self, check: dict):
        item = self.item
        pixmap = self.pixmap
        self.gameName.setText(item.title)

        self.closeButton.clicked.connect(self.close)

        self.gameImage.setPixmap(pixmap)
        list_review = item.details.info.reviews

        for i in range(len(list_review)):
            score = list_review[i].score
            count = list_review[i].count

            if score != None:
                if score < 50:
                    color = "red"
                elif 50 <= score < 80:
                    color = "#FFC300"
                else:
                    color = "green"

            if list_review[i].source == "Steam":
                if score != None:
                    self.steamScore.setText(str(score))
                    self.steamScore.setStyleSheet(f"color: {color};")

                if count != None:
                    self.steamCount.setText(str(count))
            elif list_review[i].source == "Metascore":
                if score != None:
                    self.metaScore.setText(str(score))
                    self.metaScore.setStyleSheet(f"color: {color};")

                if count != None:
                    self.metaCount.setText(str(count))

            elif list_review[i].source == "Metacritic":
                if score != None:
                    self.metaUserScore.setText(str(score))
                    self.metaUserScore.setStyleSheet(f"color: {color};")

                if count != None:
                    self.metaUserCount.setText(str(count))
            elif list_review[i].source == "OpenCritic":
                if score != None:
                    self.openCriticScore.setText(str(score))
                    self.openCriticScore.setStyleSheet(f"color: {color};")

                if count != None:
                    self.openCriticCount.setText(str(count))

        self.releaseDate.setText(
            "Ngày phát hành: " + str(item.details.info.releaseDate)
        )
        tags_str = "Tất cả các tags: "
        tags = item.details.info.tags
        for tag in tags:
            if tag != tags[-1]:
                tags_str += tag + ", "
            else:
                tags_str += tag
        self.tags.setText(tags_str)
        stat = item.details.info.stats
        self.rank.setText("Xếp Hạng: " + str(stat.rank))
        playerInfo = item.details.info.players
        self.recentPlayerCount.setText(
            "Lượng người chơi hiện tại: " + str(playerInfo.recent)
        )
        self.dayPlayerCount.setText(
            "Lượng người chơi trong ngày: " + str(playerInfo.day)
        )
        self.weekPlayerCount.setText(
            "Lượng người chơi trong tuần: " + str(playerInfo.week)
        )
        self.peak.setText("cùng lúc cao nhất: " + str(playerInfo.peak))

        currentPriceStr = ""
        basePriceStr = ""
        saleStr = ""
        if item.deal.price != "Free":
            currentPriceStr = str(item.deal.price.amount) + "$"
            basePriceStr = str(item.deal.regular.amount) + "$"
            saleStr = (
                str(
                    int(100 - (item.deal.price.amount / item.deal.regular.amount) * 100)
                )
                + "%"
            )

        else:
            currentPriceStr = "Free"
            basePriceStr = "Free"
            saleStr = "FREE!"

        self.latestPrice.setText("Giá hiện tại:   " + currentPriceStr)
        self.basePrice.setText("Giá gốc:   " + basePriceStr)
        self.sale.setText(saleStr)
        self.closeButton.setStyleSheet(
            """
                QPushButton {
                    border:3px solid black;
                    border-radius:5px;
                    padding-bottom: 5px;

                }
                QPushButton:hover {
                    background-color: lightgray;
                    border:4px solid black;

                }
            """
        )
        fullScreenButtons = [
            self.playCountFull,
            self.price_chart_step_lineFull,
            self.price_chart_pie_chartFull,
            self.price_chart_heatmapFull,
            self.price_chart_grouped_barFull,
            self.price_chart_column_chartFull,
            self.price_chart_boxplotFull,
        ]
        fixed_pixelfont(fullScreenButtons, 7)
        for button in fullScreenButtons:
            button.setStyleSheet(
                """
                QPushButton {
                    border:3px solid black;
                    border-radius:5px;
                    padding-bottom: 5px;

                }
                QPushButton:hover {
                    background-color: lightgray;
                    border:4px solid black;

                }
            """
            )

        # chart playerCount
        playerCountUrl = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["PC"] == True:
            playerCountUrl = "http://127.0.0.1:5500/playersCharts/playersCount.html"
        self.playerCount_web_view = QWebEngineView(self)
        self.playerCount_web_view.load(QUrl(playerCountUrl))
        self.playerCountcontainer = self.findChild(QWidget, "playersCountChart")
        PlayerCountlayout = QVBoxLayout(self.playerCountcontainer)
        self.playerCountcontainer.setLayout(PlayerCountlayout)
        self.playerCountcontainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        PlayerCountlayout.addWidget(self.playerCount_web_view)

        # chart  price_chart_step_line
        price_chart_step_line_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_step_line_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_step_line.html"
            )
        self.price_chart_step_line_web_view = QWebEngineView(self)
        self.price_chart_step_line_web_view.load(QUrl(price_chart_step_line_Url))
        self.price_chart_step_lineContainer = self.findChild(
            QWidget, "price_chart_step_line"
        )
        price_chart_step_line_Layout = QVBoxLayout(self.price_chart_step_lineContainer)
        self.price_chart_step_lineContainer.setLayout(price_chart_step_line_Layout)
        self.price_chart_step_lineContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_step_line_Layout.addWidget(self.price_chart_step_line_web_view)

        # chart  price_chart_pie_chart
        price_chart_pie_chart_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_pie_chart_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_pie.html"
            )
        self.price_chart_pie_chart_web_view = QWebEngineView(self)
        self.price_chart_pie_chart_web_view.load(QUrl(price_chart_pie_chart_Url))
        self.price_chart_pie_chartContainer = self.findChild(
            QWidget, "price_chart_pie_chart"
        )
        price_chart_pie_chart_Layout = QVBoxLayout(self.price_chart_pie_chartContainer)
        self.price_chart_pie_chartContainer.setLayout(price_chart_pie_chart_Layout)
        self.price_chart_pie_chartContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_pie_chart_Layout.addWidget(self.price_chart_pie_chart_web_view)

        # chart  price_chart_heatmap
        price_chart_heatmap_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_heatmap_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_heatmap.html"
            )
        self.price_chart_heatmap_web_view = QWebEngineView(self)
        self.price_chart_heatmap_web_view.load(QUrl(price_chart_heatmap_Url))
        self.price_chart_heatmapContainer = self.findChild(
            QWidget, "price_chart_heatmap"
        )
        price_chart_heatmap_Layout = QVBoxLayout(self.price_chart_heatmapContainer)
        self.price_chart_heatmapContainer.setLayout(price_chart_heatmap_Layout)
        self.price_chart_heatmapContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_heatmap_Layout.addWidget(self.price_chart_heatmap_web_view)

        # chart  price_chart_grouped_bar
        price_chart_grouped_bar_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_grouped_bar_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_grouped_bar.html"
            )
        self.price_chart_grouped_bar_web_view = QWebEngineView(self)
        self.price_chart_grouped_bar_web_view.load(QUrl(price_chart_grouped_bar_Url))
        self.price_chart_grouped_barContainer = self.findChild(
            QWidget, "price_chart_grouped_bar"
        )
        price_chart_grouped_bar_Layout = QVBoxLayout(
            self.price_chart_grouped_barContainer
        )
        self.price_chart_grouped_barContainer.setLayout(price_chart_grouped_bar_Layout)
        self.price_chart_grouped_barContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_grouped_bar_Layout.addWidget(self.price_chart_grouped_bar_web_view)

        # chart  price_chart_column_chart
        price_chart_column_chart_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_column_chart_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_column.html"
            )
        self.price_chart_column_chart_web_view = QWebEngineView(self)
        self.price_chart_column_chart_web_view.load(QUrl(price_chart_column_chart_Url))
        self.price_chart_column_chartContainer = self.findChild(
            QWidget, "price_chart_column_chart"
        )
        price_chart_column_chart_Layout = QVBoxLayout(
            self.price_chart_column_chartContainer
        )
        self.price_chart_column_chartContainer.setLayout(
            price_chart_column_chart_Layout
        )
        self.price_chart_column_chartContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_column_chart_Layout.addWidget(
            self.price_chart_column_chart_web_view
        )

        # chart  price_chart_boxplot
        price_chart_boxplot_Url = "http://127.0.0.1:5500/playersCharts/ERROR.html"
        if check["DF"] == True:
            price_chart_boxplot_Url = (
                "http://127.0.0.1:5500/PriceChart/price_chart_boxplot.html"
            )
        self.price_chart_boxplot_web_view = QWebEngineView(self)
        self.price_chart_boxplot_web_view.load(QUrl(price_chart_boxplot_Url))
        self.price_chart_boxplotContainer = self.findChild(
            QWidget, "price_chart_boxplot"
        )
        price_chart_boxplot_Layout = QVBoxLayout(self.price_chart_boxplotContainer)
        self.price_chart_boxplotContainer.setLayout(price_chart_boxplot_Layout)
        self.price_chart_boxplotContainer.setStyleSheet(
            """
            QWidget {
                border: 5px solid black;

            }
        """
        )
        price_chart_boxplot_Layout.addWidget(self.price_chart_boxplot_web_view)

        self.playerCountFullScreenStage = ChartFullScreen(playerCountUrl)
        self.price_chart_boxplot_FullScreenStage = ChartFullScreen(
            price_chart_boxplot_Url
        )
        self.price_chart_column_chart_FullScreenStage = ChartFullScreen(
            price_chart_column_chart_Url
        )
        self.price_chart_grouped_bar_FullScreenStage = ChartFullScreen(
            price_chart_grouped_bar_Url
        )
        self.price_chart_heatmap_FullScreenStage = ChartFullScreen(
            price_chart_heatmap_Url
        )
        self.price_chart_pie_chart_FullScreenStage = ChartFullScreen(
            price_chart_pie_chart_Url
        )
        self.price_chart_step_line_FullScreenStage = ChartFullScreen(
            price_chart_step_line_Url
        )

        self.playCountFull.clicked.connect(
            self.playerCountFullScreenStage.showFullScreen
        )
        self.price_chart_boxplotFull.clicked.connect(
            self.price_chart_boxplot_FullScreenStage.showFullScreen
        )
        self.price_chart_column_chartFull.clicked.connect(
            self.price_chart_column_chart_FullScreenStage.showFullScreen
        )
        self.price_chart_grouped_barFull.clicked.connect(
            self.price_chart_grouped_bar_FullScreenStage.showFullScreen
        )
        self.price_chart_heatmapFull.clicked.connect(
            self.price_chart_heatmap_FullScreenStage.showFullScreen
        )
        self.price_chart_pie_chartFull.clicked.connect(
            self.price_chart_pie_chart_FullScreenStage.showFullScreen
        )
        self.price_chart_step_lineFull.clicked.connect(
            self.price_chart_step_line_FullScreenStage.showFullScreen
        )

        self.loading_screen.hide()


class chartLoaderThread(QThread):
    data_loaded = pyqtSignal()

    def __init__(self, convertType: str):
        super().__init__()
        self.convertType = convertType

    def run(self):

        BCconvert.getCategory(self.convertType)
        self.data_loaded.emit()


class gameDataLoaderThread(QThread):
    data_loaded = pyqtSignal(object)
    data_unloaded = pyqtSignal()

    def __init__(self, item):
        super().__init__()
        self.item = item

    def run(self):
        try:

            gamecount = PCconvert.GameCount(self.item.title, self.item.steam_id)
            gamePriceData = DFConvert.visualize_PriceChart(self.item.id)

            if gamecount is not None or gamePriceData is not None:
                checked = {"PC": False, "DF": False}
                if gamecount.check:
                    checked["PC"] = True
                if gamePriceData:
                    checked["DF"] = True
                self.data_loaded.emit(checked)
            else:
                self.data_unloaded.emit()
        except Exception as e:
            print(e)
            self.data_unloaded.emit()


class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(object)

    def run(self):

        daily_game = GetDaiLyGames("VN", 15, (20, 6, 16, 35, 37, 61, 24))
        self.data_loaded.emit(daily_game)


class LoadingScreen:
    text = QWidget()

    def __init__(self, parentSelf):
        self.text = QWidget(parentSelf)
        self.text.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

        loading_label = QLabel("Đang tải, vui lòng chờ...", self.text)
        pixelfont.setPointSize(10)
        loading_label.setFont(pixelfont)
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: white; font-size: 18px;")

        loading_layout = QVBoxLayout(self.text)
        loading_layout.setSpacing(0)
        loading_layout.addWidget(loading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.text.setFixedSize(parentSelf.size())

    def hide(self):
        self.text.hide()

    def show(self):
        self.text.show()


class MainStage(QMainWindow):
    def __init__(self):
        super(MainStage, self).__init__()

        uic.loadUi("test1.ui", self)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.ReloadButton.triggered.connect(self.reload)
        chartRace_actions = {
            self.chartsAll: "All",
            self.chartsAnime: "Anime",
            self.chartsHorror: "Horror",
            self.chartsSinglePlayer: "Singleplayer",
            self.chartsRacing: "Racing",
            self.chartsSandbox: "Sandbox",
            self.chartsSports: "Sports",
            self.chartsVisualNovel: "VisualNovel",
            self.SteamUserChart: "steamUsers",
        }

        for action, chart_type in chartRace_actions.items():
            action.triggered.connect(lambda _, t=chart_type: self.showChartRace(t))

        fixed_pixelfont([self.menubar, self.ReloadButton], 8)
        chartRace_names = [
            "chartsAll",
            "chartsSinglePlayer",
            "chartsAnime",
            "chartsRacing",
            "chartsSandbox",
            "chartsVisualNovel",
            "chartsSports",
            "chartsHorror",
            "SteamUserChart",
        ]
        objects = [getattr(self, name) for name in chartRace_names]
        fixed_pixelfont(objects, 8)
        self.setWindowTitle("ValvesPalTest")
        self.setGeometry(150, 60, 1280, 720)
        self.setFixedSize(1280, 720)

        self.create_loading_screen()

        self.start_loading()

    def create_loading_screen(self):

        self.loading_screen = LoadingScreen(self).text
        self.loading_screen.hide()

    def show_loading_screen(self):

        self.loading_screen.show()

    def hide_loading_screen(self):

        self.loading_screen.hide()

    def start_loading(self):

        self.show_loading_screen()

        self.loader_thread = DataLoaderThread()
        self.loader_thread.data_loaded.connect(self.display_games)
        self.loader_thread.start()

    def display_games(self, daily_game):
        self.hide_loading_screen()

        if hasattr(self, "container"):
            QWidget().setLayout(self.layout)

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)

        self.searchBar = SearchBar(self)
        for item in daily_game.game_list:
            item_layout = QHBoxLayout()

            image_game = QLabel()
            pixmap = get_pixmap_from_url(item.logo)
            if pixmap:
                image_game.setPixmap(
                    pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                )
            image_game.setFixedSize(100, 100)

            text_container = QWidget()
            text_layout = QHBoxLayout(text_container)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_container.setStyleSheet(
                """
                QWidget {
                    background-color: white;
                    padding: 10px;
                }
                QWidget:hover {
                    background-color: lightgray;
                    border: 3px solid black;
                }
            """
            )

            game_name = QLabel(item.title)
            pixelfont.setPointSize(8)
            game_name.setFont(pixelfont)
            game_name.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            game_name.setWordWrap(True)
            game_name.setAlignment(Qt.AlignmentFlag.AlignTop)
            game_name.setFixedHeight(100)
            game_name.setFixedWidth(300)
            game_name.setEnabled(False)
            game_name.setStyleSheet("color: black;background-color: rgba(0, 0, 0, 0);")

            curentPrice = QLabel("Giá Hiện tại: " + str(item.deal.price.amount) + " $")
            curentPrice.setFont(pixelfont)
            curentPrice.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            curentPrice.setMinimumHeight(90)
            curentPrice.setEnabled(False)
            curentPrice.setStyleSheet(
                "color: black;background-color: rgba(0, 0, 0, 0);"
            )

            basePrice = QLabel("Giá Gốc: " + str(item.deal.regular.amount) + " $")
            basePrice.setFont(pixelfont)
            basePrice.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            basePrice.setMinimumHeight(90)
            basePrice.setEnabled(False)
            basePrice.setStyleSheet("color: black;background-color: rgba(0, 0, 0, 0);")

            sale = QLabel(
                "Giảm: "
                + str(
                    int(100 - (item.deal.price.amount / item.deal.regular.amount) * 100)
                )
                + " %"
            )
            sale.setFont(pixelfont)
            sale.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sale.setMinimumHeight(90)
            sale.setEnabled(False)
            sale.setStyleSheet("color: black;background-color: rgba(0, 0, 0, 0);")

            text_layout.addWidget(game_name)
            text_layout.addWidget(curentPrice)
            text_layout.addWidget(basePrice)
            text_layout.addWidget(sale)

            text_container.mousePressEvent = (
                lambda event, item=item, pixmap=pixmap: self.game_clicked(item, pixmap)
            )
            item_layout.addWidget(image_game)
            item_layout.addWidget(text_container)
            self.layout.addLayout(item_layout)

        self.scrollArea.setWidget(self.container)
        self.scrollArea.setStyleSheet(verticalScrollBarStyle)

    def showChartRace(self, chart_type):
        self.chartStages = getattr(self, "chartStages", {})
        if chart_type not in self.chartStages:
            self.chartStages[chart_type] = ChartStage(chart_type, self)
        self.chartStages[chart_type].show()

    def reload(self):

        self.start_loading()

    def game_clicked(self, item, pixmap: QPixmap):

        self.new_stage = gameStage(item, pixmap, self)
        self.new_stage.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip
        )
        self.new_stage.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.new_stage.show()

    def game_clicked_onSearch(self, item):
        pixmap = get_pixmap_from_url(item.logo)
        self.new_stage = gameStage(item, pixmap, self)
        self.new_stage.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip
        )
        self.new_stage.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.new_stage.show()


window = MainStage()
window.show()
app.exec()
