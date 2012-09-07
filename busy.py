import math, sys
from PyQt4.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt4.QtGui import *

from utils import resource_path



class BusySpinnerWidget(QWidget):

    def __init__(self, parent=None):
        super(BusySpinnerWidget, self).__init__(parent)

        self.setMinimumSize(50, 50)


    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(self.palette().color(QPalette.Highlight)))


        num = 8

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(360.0/num * (self.counter % num))

        for i in range(num):

            s = 3
            s += i


            x =  20 * math.cos(2.0 * math.pi * i / num) - s/2.0
            y =  20 * math.sin(2.0 * math.pi * i / num) - s/2.0


            painter.drawEllipse(
                x,
                y,
                s, s)
        painter.end()




    def showEvent(self, event):
        self.timer = self.startTimer(100)
        self.counter = 0

    def hideEvent(self, event):
        self.killTimer(self.timer)


    def timerEvent(self, event):

        self.counter += 1
        self.update()



class MessageWidget(QWidget):


    retryClicked = pyqtSignal()

    def __init__(self, parent=None):
        super(MessageWidget, self).__init__(parent)

        self.setAutoFillBackground(True)

        self.spinner = BusySpinnerWidget(self)
        self.icon = QLabel(self)
        self.icon.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.retry = QPushButton('Retry', self)
        self.retry.setMaximumWidth(100)
        self.retry.hide()

        self.retry.clicked.connect(self.retryClicked)

        self._createLayout()

    def setLoading(self, msg):
        self.icon.hide()
        self.retry.hide()
        self.spinner.show()
        self.setMessage(msg)


    def setError(self, msg):
        self.spinner.hide()
        self._setIcon(resource_path('img/error.png'))
        self.icon.show()
        self.setMessage('<font color="red">'+msg+'</font>')

    def setDisconnected(self, msg):
        self.spinner.hide()
        self._setIcon(resource_path('img/connect.png'))
        self.icon.show()
        self.setMessage(msg)


    def setMessage(self, msg):
        self.label.setText(msg)


    def _setIcon(self, icon):
        self.icon.setPixmap(QPixmap(icon))

    def _createLayout(self):

        l = QVBoxLayout()

        l.addStretch()
        l.addWidget(self.spinner)
        l.addWidget(self.icon)
        l.addSpacing(15)
        l.addWidget(self.label)
        l.addSpacing(10)
        l.addWidget(self.retry, 0, Qt.AlignCenter)
        l.addStretch()

        self.setLayout(l)


