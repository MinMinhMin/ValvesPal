import sqlite3
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QLineEdit
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt
from searchBar import *
from game_info import GameView
from getPrice import GetPrice
from game import *

dic = {}


class SearchWindow(QWidget):
    def __init__(self, window, windowParent):
        super().__init__()
        font_id = QFontDatabase.addApplicationFont("FVF_Fernando_08.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        pixelfont = QFont(font_family, 10)
        self.setWindowTitle("Search Window")
        self.setWindowFlag(Qt.WindowType.ToolTip)

        SearchWindow.process()

        big_layout = QVBoxLayout()
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        self.results_layout = QVBoxLayout()  # Layout to hold search result buttons

        self.window = window
        self.windowParent = windowParent

        big_layout.addLayout(layout1)
        big_layout.addLayout(self.results_layout)
        big_layout.addLayout(layout2)

        close_button = QPushButton("Close")
        close_button.setFont(pixelfont)
        close_button.clicked.connect(self.close)

        self.searchBar = QLineEdit()
        self.searchBar.textChanged.connect(self.on_text_changed)

        layout1.addWidget(self.searchBar)
        layout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout2.addWidget(close_button)
        layout2.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setLayout(big_layout)

    def on_text_changed(self, text):
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if text != "":
            list_game_title = SearchGame(text).all
            for title in list_game_title:

                button = QPushButton(title)

                font_id = QFontDatabase.addApplicationFont("FVF_Fernando_08.ttf")
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                pixelfont = QFont(font_family, 8)

                button.setFixedHeight(50)
                button.setFont(pixelfont)
                button.setStyleSheet(
                    """
                QPushButton {
                    color: black;
                    background-color: white;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                    border: 3px solid black;
                }
            """
                )
                button.clicked.connect(
                    lambda checked, t=title: self.on_result_clicked(t)
                )
                self.results_layout.addWidget(button)

    def on_result_clicked(self, title):
        print(
            f"You clicked on: {title} with id:{dic[title]}"
        )  # Replace with any action you want
        deal = GetPrice(dic[title]).best_deal
        game = Game(dic[title], None, title, deal)
        self.windowParent.game_clicked_onSearch(game)

    def closeEvent(self, event):
        print("Search window closed")  # Handle any cleanup if needed
        self.window.setFocus()
        self.window.setEnabled(True)
        self.window.sub_window = None
        self.window.remove_blur()
        event.accept()  # Accept the event to close the window

    def process():
        conn = sqlite3.connect("SearchBar_game.db")
        cursor = conn.cursor()

        query = "SELECT Title, id FROM game_info"
        cursor.execute(query)

        results = cursor.fetchall()
        for row in results:
            dic[row[0]] = row[1]
        conn.close()


class SearchGame:
    def __init__(self, prefix):
        self.all = self.find_titles_by_prefix(prefix)

    def find_titles_by_prefix(self, prefix):
        conn = sqlite3.connect("SearchBar_game.db")
        cursor = conn.cursor()

        query = "SELECT Title, id FROM game_info WHERE Title LIKE ? limit 10"
        cursor.execute(query, (f"{prefix}%",))

        results = cursor.fetchall()
        conn.close()

        return [title[0] for title in results]


# game_info = GameView(dic[title])
# deal=GetPrice(dic[title]).best_deal
# game=Game(dic[title],None,title,deal,game_info)
# game là đối tượng chứa thông tin( phải dùng cả 3 dòng trên)
