from PyQt6.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLabel,
    QGraphicsBlurEffect,
    
)
from PyQt6.QtGui import QIcon,QFontDatabase,QFont
from PyQt6.QtCore import Qt
from SearchWindow import SearchWindow


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.parent():  # Ensure there's a parent (the SearchBar)
            self.parent().open_new_window()  # Call method to open a new window

            self.parent().sub_window.setFixedHeight(
                int(self.parent().window.height() * 0.8)
            )
            self.parent().sub_window.setFixedWidth(
                int(self.parent().window.width() * 0.8)
            )

            main_rect = (
                self.parent().window.geometry()
            )  
            sub_width = (
                self.parent().sub_window.width()
            )  
            sub_height = (
                self.parent().sub_window.height()
            )  

            self.parent().sub_window.move(
                main_rect.x() + (main_rect.width() - sub_width) // 2,
                main_rect.y() + (main_rect.height() - sub_height) // 2,
            )

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        print("Search bar lost focus")


class SearchBar(QWidget):
    def __init__(self, window):
        super().__init__()
        self.search_input = CustomLineEdit(self)
        font_id = QFontDatabase.addApplicationFont("FVF_Fernando_08.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        pixelfont = QFont(font_family,10)  
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFont(pixelfont)

        self.window = window
        self.sub_window = None
        self.init_ui()
        self.place()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(0)  

        
        icon_label = QLabel(self)
        icon = QIcon.fromTheme("edit-find")  
        icon_label.setPixmap(icon.pixmap(20, 20))  

        layout.addWidget(self.search_input)
        layout.addWidget(icon_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

    def resizeEvent(self, event):
        self.search_input.setFixedWidth(int(self.width() * 0.25))
        super().resizeEvent(event)

    def apply_blur(self):
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(10)
        self.window.centralWidget().setGraphicsEffect(blur_effect)

    def remove_blur(self):
        self.window.centralWidget().setGraphicsEffect(None)

    def open_new_window(self):
        if self.sub_window is None:  
            self.sub_window = SearchWindow(
                self,self.window
            )  
            self.sub_window.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )  

            self.apply_blur()
        self.sub_window.show()  

    def place(self):
        

        # Create and add SearchBar at the top
        self.window.layout.addWidget(self)

      