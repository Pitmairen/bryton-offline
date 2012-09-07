
import urllib
import json
import logging

from PyQt4.QtCore import (
    Qt, pyqtSignal, QObject, QUrl, QTimer
)
from PyQt4.QtGui import (
    QDialog, QVBoxLayout,
    QDialogButtonBox, QLabel,
    QMessageBox, QProgressBar, QLineEdit
)
from PyQt4.QtNetwork import (
    QNetworkAccessManager, QNetworkRequest,
)

log = logging.getLogger(__name__)


def upload_to_brytonsport(bbclient, parent, **kw):


    dialog = UploadDialog(bbclient, parent=parent, **kw)

    dialog.exec_()





class UploadDialog(QDialog):


    def __init__(self, bbclient, parent=None, session_id=None, username=None, password=None):
        super(UploadDialog, self).__init__(parent,
                Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint)

        self.session_id = session_id
        self.username = username
        self.password = password
        self._first_auth = True


        self.total_progress = QProgressBar(self)
        self.total_progress.setRange(0, 100)
        self.total_progress.setValue(0)
        self.total_progress.setFormat('%p%')


        self.status_msg = QLabel('Starting upload', self)


        self.setWindowTitle('Uploading')


        self._createLayout()


        self.upload = BrytonSportUpload(bbclient, parent=self)

        self.upload.authNeeded.connect(self._onAuthNeeded)
        self.upload.totalProgress.connect(self.total_progress.setValue)
        self.upload.statusMessage.connect(self.status_msg.setText)
        self.upload.finished.connect(self._onFinished)
        self.upload.failed.connect(self._onError)
        # self.upload.start()

        QTimer.singleShot(100, self.upload.start)




    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(self.status_msg)
        l.addWidget(self.total_progress)

        self.setLayout(l)



    def _onAuthNeeded(self):

        if self._first_auth and self.username is not None and self.password is not None:
            self._first_auth = False
            self.upload.authenticate(self.username, self.password)
            return


        d = AuthDialog(self)

        if d.exec_() == QDialog.Accepted:
            u, p = d.getValues()
            self.upload.authenticate(u, p)
        else:
            self.accept()


    def _onFinished(self):

        QMessageBox.information(self, 'Upload Finished', 'The tracks was successfully uploaded.')

        self.accept()

    def _onError(self):
        QMessageBox.warning(self, 'Upload Failed', 'The upload failed with an unknown error.')
        self.accept()












class AuthDialog(QDialog):


    def __init__(self, parent):

        super(QDialog, self).__init__(parent)

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Your email')
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Your password')

        self._buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)


        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        self.setWindowTitle('Authentication')
        self.resize(300, 150)

        self._createLayout()

    def getValues(self):
        return str(self.username.text()), str(self.password.text())


    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(QLabel('Email:'))
        l.addWidget(self.username)
        l.addWidget(QLabel('Password:'))
        l.addWidget(self.password)

        l.addWidget(self._buttons)

        self.setLayout(l)






class BrytonSportUpload(QObject):


    LOGIN = 'http://www.brytonsport.com/login'


    authNeeded = pyqtSignal()
    statusMessage = pyqtSignal(str)
    totalProgress = pyqtSignal(int)
    finished = pyqtSignal()
    failed = pyqtSignal()


    def __init__(self, bbclient, parent, session_id=None):
        super(BrytonSportUpload, self).__init__(parent)
        self.bbclient = bbclient
        self.session_id = session_id
        self.network_manager = QNetworkAccessManager(self)


        self.bbclient.uploadFailed.connect(self.failed)
        self.bbclient.uploadFinished.connect(self.finished)
        self.bbclient.uploadProgress.connect(self.totalProgress)


    def start(self):
        self._doAuthenticate()


    def authenticate(self, username, password):


        req = QNetworkRequest(QUrl(self.LOGIN))
        req.setHeader(QNetworkRequest.ContentTypeHeader,
                "application/x-www-form-urlencoded")

        log.debug('Sending auth request')
        self.reply = self.network_manager.post(req, urllib.urlencode({
            'data[account]' : username,
            'data[passwd]' : password,
            }))

        self.reply.finished.connect(self._onAuthenticated)


    def _doAuthenticate(self):

        if self.session_id is not None:
            self._doUpload(self.session_id)
            return

        log.debug('Auth needed')
        self.statusMessage.emit('Authenticating')
        self.authNeeded.emit()


    def _onAuthenticated(self):


        data = self._loadJson(str(self.reply.readAll()))

        if data is None or not 'User' in data:
            log.debug('Auth failed (response: %s)', data)
            self._doAuthenticate()
            return
        log.debug('Auth OK')
        ses = data['User']['SessionId']

        self._doUpload(ses)

    def _doUpload(self, session_id):

        self.statusMessage.emit('Uploading history')
        self.bbclient.uploadToBrytonSport(session_id)



    def _loadJson(self, data):
        try:
            return json.loads(data)
        except ValueError, e:
            return None


