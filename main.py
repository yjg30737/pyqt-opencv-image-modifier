import cv2
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QGraphicsView, \
    QFileDialog, QGraphicsItem

from PyQt5.QtCore import Qt, QRectF, QRect
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


# TODO
# set padding to make it look better
# use QOpenGLWidget to boost the performance

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__initVal()

    def __initVal(self):
        self.__scene = QGraphicsScene()

    def setFilename(self, filename: str):
        # remove previous one
        self.__scene.clear()

        # set the scene rect to size of the image and set the scene which has image
        p = QPixmap(filename)
        size = p.size()
        self.__scene.setSceneRect(0, 0, size.width(), size.height())
        self.__scene.addPixmap(p)
        self.setScene(self.__scene)

        # fit the image to the view
        self.fitInView(self.__scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    # fit the image to the view AFTER window size got resized
    def resizeEvent(self, e):
        self.fitInView(self.__scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        return super().resizeEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('OpenCV with PyQt')

        openBtn = QPushButton('Open')
        openBtn.clicked.connect(self.__open)

        self.__hBtn = QPushButton('FlipH')
        self.__vBtn = QPushButton('FlipV')
        self.__dBtn = QPushButton('FlipD')
        self.__sBtn = QPushButton('Symmetrize')

        self.__hBtn.setEnabled(False)
        self.__vBtn.setEnabled(False)
        self.__dBtn.setEnabled(False)
        self.__sBtn.setEnabled(False)

        self.__hBtn.clicked.connect(self.__transformH)
        self.__vBtn.clicked.connect(self.__transformV)
        self.__dBtn.clicked.connect(self.__transformD)
        self.__sBtn.clicked.connect(self.__convertOpencv)

        lay = QHBoxLayout()
        lay.addWidget(self.__hBtn)
        lay.addWidget(self.__vBtn)
        lay.addWidget(self.__dBtn)
        lay.addWidget(self.__sBtn)
        lay.setContentsMargins(0, 0, 0, 0)
        toolWidget = QWidget()
        toolWidget.setLayout(lay)

        self.__view = GraphicsView()
        self.__view.setRenderHint(QPainter.Antialiasing)
        self.__view.setRenderHint(QPainter.SmoothPixmapTransform)

        lay = QVBoxLayout()
        lay.addWidget(openBtn)
        lay.addWidget(toolWidget)
        lay.addWidget(self.__view)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

    def __open(self):
        filename = QFileDialog.getOpenFileName(self, 'Select the Image', '', 'Image File (*.jpg *.png *.bmp)')
        if filename[0]:
            filename = filename[0]
            self.__view.setFilename(filename)

            self.__hBtn.setEnabled(True)
            self.__vBtn.setEnabled(True)
            self.__dBtn.setEnabled(True)
            self.__sBtn.setEnabled(True)

    def __transformH(self):
        transform = self.__view.transform()
        transform.scale(-1, 1)
        self.__view.setTransform(transform)

    def __transformV(self):
        transform = self.__view.transform()
        transform.scale(1, -1)
        self.__view.setTransform(transform)

    def __transformD(self):
        transform = self.__view.transform()
        transform.rotate(180)
        self.__view.setTransform(transform)

    def __convertOpencv(self):
        items = self.__view.items()
        if len(items) > 0:
            # get the QImage out of QGraphicsItem
            item = items[0]
            p = item.pixmap()
            img = p.toImage()

            # convert into numpy array
            rect = QRect(img.rect())
            ptr = img.bits()
            ptr.setsize(rect.width() * rect.height() * 4)
            img = np.array(ptr, np.uint8).reshape(rect.height(), rect.width(), 4)

            rows, cols = img.shape[:2]
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
            dst = cv2.warpAffine(img, M, (cols, rows))

            cv2.imshow('YY', dst)
            cv2.waitKey(0)
            cv2.destroyAllWindows()




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()