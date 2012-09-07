
import sys
import os

from math import radians, sqrt, sin, cos, atan2

from PyQt4.QtGui import QProgressBar, QDialog, QLabel, QVBoxLayout


if getattr(sys, 'frozen', None):
     _basedir = sys._MEIPASS
else:
     _basedir = os.path.dirname(__file__)


def resource_path(name):

    return os.path.join(_basedir, name)



def indent_element_tree(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_element_tree(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def stripws_element_tree(elem):
    if len(elem):
        if elem.text and not elem.text.strip():
            elem.text = None
        if elem.tail and not elem.tail.strip():
            elem.tail = None
        for elem in elem:
            stripws_element_tree(elem)
        if elem.tail and not elem.tail.strip():
            elem.tail = None
    else:
        if elem.tail and not elem.tail.strip():
            elem.tail = None


def geo_distance(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon1 - lon2

    EARTH_R = 6372.8

    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)


    return EARTH_R * c





class ProgressDialog(QDialog):


    def __init__(self, title, description, parent):

        super(ProgressDialog, self).__init__(parent)

        self.setWindowTitle(title)


        self.label = QLabel(description, self)
        self.label.setContentsMargins(2, 0, 0, 0)
        self.progress = QProgressBar(self)

        self._createlayout()

    def _createlayout(self):


        l = QVBoxLayout()

        l.addWidget(self.label)
        l.addWidget(self.progress)


        self.setLayout(l)
