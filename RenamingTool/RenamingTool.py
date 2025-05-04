import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QIcon

class DynamicWidgets(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dynamic Widgets Example")
        self.layout = QVBoxLayout()

        self.add_button = QPushButton("Add Text Field")
        self.add_button.clicked.connect(self.add_text_field)
        self.add_button.setIcon(QIcon('./Icons/add.png'))
        self.layout.addWidget(self.add_button)

        self.text_fields = []

        self.setLayout(self.layout)

    def add_text_field(self):
        text_field = QLineEdit()
        self.layout.addWidget(text_field)
        self.text_fields.append(text_field)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DynamicWidgets()
    window.show()
    sys.exit(app.exec_())