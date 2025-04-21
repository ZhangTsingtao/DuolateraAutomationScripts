#GUI
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QIntValidator

import sys

#image processing
import cv2
import numpy as np

class DropArea(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Drop source albedo image here")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 25px;")
        self.setAcceptDrops(True)  # Enable drops

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet("border: 2px solid #66afe9; border-radius: 5px; padding: 25px; background-color: #f0f8ff;")
            event.acceptProposedAction()
            event.accept()
        else:
            event.ignore()
        
    def dragLeaveEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 25px;")
            event.accept()
        else:
            event.ignore()
        
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Albedo to RGB Channel Mask Converter")

        #widget var
        self.convertButtonDefaultText = "Convert"

        #widget components
        self.dropImageFile = DropArea()

        self.labelChannelAmount = QLabel("Total color amount")
        
        self.inputChannelAmount = QLineEdit()
        self.inputChannelAmount.setValidator(QIntValidator(1, 21))#limit the input is only int
        self.inputChannelAmount.setText("6")

        self.button = QPushButton(self.convertButtonDefaultText)
        self.button.clicked.connect(self.onButtonClicked)

        self.labelInputInstructions = QLabel("After images are shown, press any key on keyboard to continue")

        #layout
        layout = QVBoxLayout()
        layout.addWidget(self.dropImageFile)
        layout.addWidget(self.labelChannelAmount)
        layout.addWidget(self.inputChannelAmount)
        layout.addWidget(self.button)
        layout.addWidget(self.labelInputInstructions)

        container = QWidget()
        container.setLayout(layout)

        self.setMinimumSize(QSize(600, 300))
        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def onButtonClicked(self):
        print("conversion funcion")
        self.button.setText("Converting...")
        self.button.setEnabled(False)

        #check k input
        
        
        file_path = self.dropImageFile.text()
        if not self.inputChannelAmount.text():
            QMessageBox.critical(self, "Invalid Total Color Amount input", f"Total Color Amount is empty")
            return
        k = int(self.inputChannelAmount.text())
        
        self.quantizeColors(file_path, k)

        self.button.setText(self.convertButtonDefaultText)
        self.button.setEnabled(True)



    def quantizeColors(self, image_path, k=6):

        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            #raise ValueError(f"Could not read image at {image_path}")
            QMessageBox.critical(self, "File Path Error", f"Could not read image at {image_path}")
            return

        # Convert to RGB (OpenCV uses BGR by default)
        imageRgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Reshape the image to a 2D array of pixels
        pixels = imageRgb.reshape(-1, 3).astype(np.float32)


        # Define criteria for K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        # Apply K-means clustering
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        # Convert back to uint8
        centers = np.uint8(centers)

        originalCenters = centers #save the original copy

        print(f"Image resolution: {image.shape[1]} x {image.shape[0]}")
        print(f"Clustered values: \n {centers}")
        print(len(labels))
        self.show_image(originalCenters, labels, imageRgb, "clustered")

        # First, set centers to all [0,0,0]
        for i, center in enumerate(centers):
            centers[i] = [0, 0, 0]

        # Then, iterate through k, store every 3 in a mask
        i = 0
        j = i
        while i < k:
            if j == 0: 
                centers[i] = [255, 0, 0]
            elif j == 1:
                centers[i] = [0, 255, 0]
            elif j == 2:
                centers[i] = [0, 0, 255]

            i += 1
            j = i % 3

            if j == 0: # time to save a mask
                maskIndex = int(i/3 - 1)
                print(maskIndex)
                maskBgr = self.show_image(centers, labels, imageRgb, f"Mask_{maskIndex}")

                outputPath = f"{image_path.rsplit('.', 1)[0]}_Mask_{maskIndex}.png"

                cv2.imwrite(outputPath, maskBgr)
                print(f"Quantized image saved to {outputPath}")

                # Reset centers to [0,0,0]
                for index, center in enumerate(centers):
                    centers[index] = [0, 0, 0]

        # Wait for a key press and then close
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return originalCenters
    
    def show_image(self, centers, labels, imageRgb, imageName):
        centers = np.uint8(centers)
        # Map each pixel to its corresponding center
        imageFlat = centers[labels.flatten()]
        # Reshape back to the original image shape
        image = imageFlat.reshape(imageRgb.shape)
        # Convert back to BGR for OpenCV
        imageBgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        scaledImage = cv2.resize(imageBgr, (720, 720))
        cv2.imshow(f"{imageName}", scaledImage)

        return imageBgr


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()