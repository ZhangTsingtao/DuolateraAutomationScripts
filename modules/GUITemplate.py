from PyQt5 import QtWidgets
from PyQt5 import QtCore

class DropArea(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Drop source albedo image here")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 25px;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet("border: 2px solid #66afe9; border-radius: 5px; padding: 25px; background-color: #f0f8ff;")
            event.acceptProposedAction()
            event.accept()
        else:
            event.ignore()
        
    def dragLeaveEvent(self, event):
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 25px;")
        
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                file_paths.append(file_path)
            
            self.setText(file_paths[0])
            # You can access the file path with file_paths[0] for the first file
            # Or process multiple files with file_paths list
            event.accept()
        else:
            event.ignore()
        
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 25px;")
        event.acceptProposedAction()

class DropListWidget(QtWidgets.QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.resize(600, 600)

    def dragEnterEvent(self, e):
        print("drag enter event")
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        print("drag move event")
        if e.mimeData().hasUrls():
            e.setDropAction(QtCore.Qt.DropAction.CopyAction)
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()

            links = []

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile))
                else:
                    event.ignore()
            
            self.addItems(links)
        
        else:
            event.ignore()

class WindowTemplate(QtWidgets.QMainWindow):
    #properties
    @property
    def titleName(self) -> str:
        return self._titleName
    @titleName.setter
    def titleName(self, newName:str) -> None:
        self._titleName = newName

    @property
    def windowSize(self) -> QtCore.QSize:
        return self._windowSize
    @windowSize.setter
    def windowSize(self, newSize:QtCore.QSize) -> None:
        self._windowSize = newSize

    @property
    def centralWidgetLayout(self) -> QtWidgets.QWidget:
        return self._centralWidgetLayout
    @centralWidgetLayout.setter
    def centralWidgetLayout(self, newWidget:QtWidgets.QWidget) -> None:
        self._centralWidgetLayout = newWidget

    #virtual functions meant to be overriden by subclass
    def createWidgets(self):
        pass
    def layoutWidgets(self):
        pass
    def connectWidgets(self):
        pass

    def __init__(self):
        super().__init__()
 
        self.createWidgets()
        self.layoutWidgets()
        self.connectWidgets()
        
        #set window title, size, and set central widget
        self.setWindowTitle(self._titleName)
        
        self.setMinimumSize(self._windowSize)

        container = QtWidgets.QWidget()
        container.setLayout(self._centralWidgetLayout)
        self.setCentralWidget(container)
        



# # Example implementation of the abstract class
# class TestClass(WindowTemplate):
#     _titleName = 'test window'
#     _windowSize = QtCore.QSize(600, 600)
#     _centralWidgetLayout = QtWidgets.QVBoxLayout()
#     def __init__(self):
#         super().__init__()

#     def createWidgets(self):
#         self.label = QtWidgets.QLabel("This is a test window")

#     def layoutWidgets(self):
#         self.centralWidgetLayout = QtWidgets.QVBoxLayout()
#         self.centralWidgetLayout.addWidget(self.label)

#     def connectWidgets(self):
#         return


# def main():
#     import sys
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv)

#     window = TestClass()
#     window.show()

#     app.exec()

# if __name__ == '__main__':
#     main()