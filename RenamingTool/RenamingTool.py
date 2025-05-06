from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QIcon
import os
from GUITemplate import *

class AssetTypeDropListWidget(DropListWidget):
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    assetTypeEntry = AssetTypeEntry(str(url.toLocalFile()))
                    item = QtWidgets.QListWidgetItem()
                    item.setSizeHint(assetTypeEntry.sizeHint())
                    self.addItem(item)
                    self.setItemWidget(item, assetTypeEntry)
                    
                    event.accept()
                else:
                    event.ignore()
        
        else:
            event.ignore()

class RenamingWindow(WindowTemplate):
    _titleName = 'Renaming Tool'
    _windowSize = QtCore.QSize(800, 600)
    _centralWidgetLayout = QtWidgets.QVBoxLayout()
    def __init__(self):
        super().__init__()

    def createWidgets(self):
        self.labelNameInstruction = QtWidgets.QLabel("Type in the asset name")
        self.lineEditAssetName = QtWidgets.QLineEdit()
        self.dropListWidgetFiles = AssetTypeDropListWidget()
        self.buttonRename = QtWidgets.QPushButton("Rename")
        self.buttonClear = QtWidgets.QPushButton("Clear")

    def layoutWidgets(self):
        self.centralWidgetLayout = QtWidgets.QVBoxLayout()
        self.centralWidgetLayout.addWidget(self.labelNameInstruction)
        self.centralWidgetLayout.addWidget(self.lineEditAssetName)
        self.centralWidgetLayout.addWidget(self.dropListWidgetFiles)
        self.centralWidgetLayout.addWidget(self.buttonRename)
        self.centralWidgetLayout.addWidget(self.buttonClear)

    def connectWidgets(self):
        self.buttonRename.clicked.connect(self.renameFiles)
        self.buttonClear.clicked.connect(lambda : self.dropListWidgetFiles.clear())
    
    def renameFiles(self):
        assetName = self.lineEditAssetName.text()
        if assetName == '':
            self.buttonRename.setText("Please type in asset name! Click again to Rename")
            return
        self.buttonRename.setText("Rename")
        print(assetName)
        
        # initialize a dict to avoid multiple assets with same type
        assetTypeDict = {}
        for assetType in AssetType:
            assetTypeDict[assetType.name] = 0

        # iterate through each entry 
        for i in range(self.dropListWidgetFiles.count()):
            #extract path and asset type from custom widget
            

            assetTypeEntry : AssetTypeEntry = self.dropListWidgetFiles.itemWidget(self.dropListWidgetFiles.item(i))
            if not isinstance(assetTypeEntry, AssetTypeEntry):
                print("Error: assetTypeEntry is not AssetTypeEntry class")
                return
            assetPath = assetTypeEntry.getAssetPath()
            directory = os.path.split(assetPath)[0]
            fileName = os.path.split(assetPath)[1]
            assetTypeName = assetTypeEntry.getAssetTypeName()
            filePrefix = getAssetTypePrefix(assetTypeName)
            fileRoot, fileSuffix = os.path.splitext(assetPath)
            

            #check for multiple assets of the same type
            if assetTypeDict[assetTypeName] > 0:
                fileSuffix = '_' + str(assetTypeDict[assetTypeName]) + fileSuffix
            assetTypeDict[assetTypeName] += 1

            #overwrite with new asset name with prefix
            fileName = filePrefix + assetName + fileSuffix
            newFilePath = f"{directory}/{fileName}"
            print(f"new path: {newFilePath}")

            #Rename
            os.rename(assetPath, newFilePath)
            #print("Rename Successfully")

            #After renaming, also change the path in the GUI
            assetTypeEntry.setNewAssetPath(newFilePath)

def getAssetTypePrefix(assetTypeName:str) -> str:
    if assetTypeName == AssetType.STATIC_MESH.name:
        return 'SM_'
    elif assetTypeName == AssetType.SKELETAL_MESH.name:
        return 'SKM_'
    elif assetTypeName == AssetType.ALBEDO.name:
        return 'T_Albedo_' 
    elif assetTypeName == AssetType.RGB_MASK.name:
        return 'T_Mask_'   
    elif assetTypeName == AssetType.NORMAL_MAP.name:
        return 'T_Normal_'
    else:
        print("Error: invalid asset type")
        return ''

def main():
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    window = RenamingWindow()
    window.show()

    app.exec()

if __name__ == '__main__':
    main()