
import urllib
import json
import logging

from PyQt4.QtCore import (
    Qt, QEvent, pyqtSignal, QObject, QUrl, QTimer,
)
from PyQt4.QtGui import (
    QDialog, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
    QComboBox, QDialogButtonBox, QLabel,
    QLineEdit, QDialog, QProgressBar,
    QListWidget, QListWidgetItem
)
from PyQt4.QtNetwork import (
    QNetworkAccessManager, QNetworkRequest,
)


import tcx


log = logging.getLogger(__name__)


def upload_to_strava(tracks, device_info, parent, **kw):

    d = UploadEditorDialog(tracks, parent=parent)

    if d.exec_() != QDialog.Accepted:
        return

    tracks = list(d.getValues())

    dialog = UploadDialog(tracks, device_info=device_info, parent=parent, **kw)



    dialog.exec_()





class UploadDialog(QDialog):


    def __init__(self, tracks, device_info=None, username=None, password=None, auth_token=None, parent=None):
        super(UploadDialog, self).__init__(parent)

        self.tracks = tracks

        self.username = username
        self.password = password
        self._first_auth = True

        self.total_progress = QProgressBar(self)
        self.total_progress.setRange(0, len(tracks))
        self.total_progress.setValue(0)
        self.total_progress.setFormat('%v of %m tracks uploaded')

        self.item_progress = QProgressBar(self)
        self.item_progress.setRange(0, 100)
        self.item_progress.setValue(0)
        self.item_progress.setFormat('%p%')

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.reject)

        self.status_msg = QLabel('Starting upload', self)


        self.setWindowTitle('Uploading')


        self._createLayout()


        self.upload = StravaUpload(tracks, device_info=device_info, parent=self, auth_token=auth_token)

        self.upload.authNeeded.connect(self._onAuthNeeded)
        self.upload.itemProgress.connect(self.item_progress.setValue)
        self.upload.totalProgress.connect(self.total_progress.setValue)
        self.upload.statusMessage.connect(self.status_msg.setText)
        self.upload.finished.connect(self._onFinished)



        self.rejected.connect(self._onCanceled)

        QTimer.singleShot(100, self.upload.start)

    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(self.status_msg)
        l.addWidget(self.item_progress)
        l.addWidget(self.total_progress)
        l.addWidget(self.buttons)

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
            log.debug('Auth dialog rejected')
            self._onCanceled()

    def _onFinished(self):

        res = self.upload.results

        if len(res) != len(self.tracks):
            res.extend([{'status' : 'ERROR', 'msg' : 'Canceled'}] * (len(self.tracks) - len(res)))

        log.debug('Upload finished')

        d = ResultDialog(zip(self.tracks, res), self)

        d.exec_()
        self.accept()


    def _onCanceled(self):
        log.debug('Upload canceled')
        self.upload.cancel()

        self._onFinished()


class ResultDialog(QDialog):


    def __init__(self, result, parent):

        super(QDialog, self).__init__(parent)


        self.list = QListWidget(self)
        self.list.setSelectionMode(QListWidget.NoSelection)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)


        self.buttons.accepted.connect(self.accept)

        self.setWindowTitle('Result')
        self.resize(380, 200)


        self._insertResult(result)

        self._createLayout()


    def _insertResult(self, result):

        for track, res in result:

            item = QListWidgetItem()

            item.setText('{0} - {1}'.format(track[0]['name'], res['msg']))

            if res['status'] == 'OK':
                # item.setBackground(Qt.green)
                pass
            elif res['status'] == 'ERROR':
                item.setForeground(Qt.red)


            self.list.addItem(item)



    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(self.list)

        l.addWidget(self.buttons)

        self.setLayout(l)




class AuthDialog(QDialog):


    def __init__(self, parent):

        super(QDialog, self).__init__(parent)

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Your email')
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Your password')

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)


        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle('Authentication')
        self.resize(300, 150)

        self._createLayout()

    def getValues(self):
        return str(self.username.text()), str(self.password.text())


    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(QLabel('Username:'))
        l.addWidget(self.username)
        l.addWidget(QLabel('Password:'))
        l.addWidget(self.password)

        l.addWidget(self.buttons)

        self.setLayout(l)




class UploadEditorDialog(QDialog):



    def __init__(self, tracks,  parent=None):

        super(UploadEditorDialog, self).__init__(parent)


        self.setWindowTitle('Upload to Strava')

        self.setFixedSize(300,200)

        self.tracks = tracks


        self._list_widget = QTreeWidget(self)
        self._list_widget.setColumnCount(2)
        self._list_widget.setRootIsDecorated(False)
        self._list_widget.setSortingEnabled(False)
        self._list_widget.setUniformRowHeights(True)
        self._list_widget.setSelectionMode(QTreeWidget.NoSelection)
        self._list_widget.setAlternatingRowColors(True)
        self._list_widget.header().resizeSection(0, 150)
        self._list_widget.header().hide()
        self._fillTable()


        self._buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)


        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)


        self._createLayout()



    def getValues(self):

        for t, w in zip(self.tracks, self._widgets):
            yield t, str(w.currentText())


    def eventFilter(self, o, e):

        if e.type() == QEvent.Wheel and isinstance(o, QComboBox):
            e.ignore()
            return True

        return super(UploadEditorDialog, self).eventFilter(o, e)


    def _fillTable(self):

        self._widgets = []
        for track in self.tracks:

            item = QTreeWidgetItem([track['name'], 'ride'])

            self._list_widget.addTopLevelItem(item)

            cb = QComboBox()

            cb.addItems(['ride', 'run'])
            cb.setFocusPolicy(Qt.ClickFocus)
            cb.installEventFilter(self)

            self._list_widget.setItemWidget(item, 1, cb)
            self._widgets.append(cb)


    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(self._list_widget)

        l.addWidget(self._buttons)


        self.setLayout(l)









class StravaUpload(QObject):

    LOGIN = 'https://www.strava.com/api/v2/authentication/login'
    ATHLETES_SHOW = 'http://www.strava.com/api/v2/athletes/{id}'
    UPLOAD = 'http://www.strava.com/api/v2/upload'
    UPLOAD_STATUS = 'http://www.strava.com/api/v2/upload/status/{id}'


    statusMessage = pyqtSignal(str)
    totalProgress = pyqtSignal(int)
    itemProgress = pyqtSignal(int)
    authNeeded = pyqtSignal()
    finished = pyqtSignal()


    def __init__(self, tracks, auth_token=None, device_info=None, parent=None):
        super(StravaUpload, self).__init__(parent)
        self.device_info = device_info
        self.auth_token = auth_token

        self.tracks = tracks[:]
        self.current_track = None
        self.results = []
        self.progress = 0
        self.upload_id = None
        self._aborted = False
        self.reply = None

        self.network_manager = QNetworkAccessManager(self)


    def start(self):

        self._doAuthenticate()

    def cancel(self):
        self._aborted = True
        if self.reply is not None:
            self.reply.abort()


    def authenticate(self, username, password):

        log.debug('Sending auth request')
        req = QNetworkRequest(QUrl(self.LOGIN))
        req.setHeader(QNetworkRequest.ContentTypeHeader,
                "application/x-www-form-urlencoded")

        self.reply = self.network_manager.post(req, urllib.urlencode({
            'email' : username,
            'password' : password,
            }))

        self.reply.finished.connect(self._onAuthenticated)


    def _emitProgress(self, msg, value):
        self.progressString.emit(msg)
        self.progress.emit(value)

    def _doAuthenticate(self):

        self.statusMessage.emit('Authenticating')

        if self.auth_token is None:
            log.debug('Auth needed')
            self.authNeeded.emit()
        else:
            self._uploadNext()






    def _onAuthenticated(self):

        data = self._loadJson(str(self.reply.readAll()))

        self.reply = None


        if data is None:
            log.debug('Auth request failed (response: %s)', data)
            self._doAuthenticate()
            return


        if 'error' in data:
            log.debug('Auth request failed (response: %s)', data['error'])
            self._doAuthenticate()

        elif 'token' in data:
            log.debug('Auth OK')
            self.auth_token = data['token']
            self._uploadNext()


    def _uploadNext(self):

        if self._aborted:
            return

        log.debug('Uploading next')

        self.itemProgress.emit(0)
        self.totalProgress.emit(self.progress)

        if not self.tracks:
            log.debug('Finished')
            self.finished.emit()
            return

        self.current_track = self.tracks.pop(0)

        self.progress += 1

        self._doUpload()


    def _doUpload(self):

        if self.current_track is None or self._aborted:
            return

        track, track_type = self.current_track




        self.statusMessage.emit('Uploading {0}'.format(track['name']))

        log.debug('Sending upload request (%s)', track['name'])

        # data_fields, data = bryton_gpx_to_strava_json(track['gpx'])

        data = tcx.bryton_gpx_to_tcx(track['gpx'], pretty=False, device=self.device_info)


        req = QNetworkRequest(QUrl(self.UPLOAD))
        req.setHeader(QNetworkRequest.ContentTypeHeader,
                "application/json")

        # d2 = json.loads(open('tmp/test.json').read())
        # d2['token'] = self.auth_token
        # self.reply = self.network_manager.post(req, json.dumps(d2))
        self.reply = self.network_manager.post(req, json.dumps({
            'token' : self.auth_token,
            'type' : 'tcx',
            'data' : data,
            'activity_type' : track_type,
            }))

        self.reply.finished.connect(self._onUploaded)

    def _onUploaded(self):

        data = self._loadJson(str(self.reply.readAll()))

        self.reply = None
        if data is None:
            log.debug('Upload failed (response: %s)', data)
            self._uploadFailed('Unknown error')
        elif 'error' in data:
            log.debug('Upload failed (%s)', data['error'])
            self._uploadFailed(data['error'])
        else:
            log.debug('Upload OK (%s)', data['upload_id'])
            self.upload_id = data['upload_id']
            self.statusMessage.emit('Checking upload status')
            QTimer.singleShot(2000, self._checkUpload)


            # self._progress += 1
            # self.tracks.pop(0)
            # self.progress.emit(self._progress)
            # self.upload()


    def _uploadFailed(self, msg):
        self.results.append({
            'status' : 'ERROR',
            'msg' : 'Failed: ' + msg,
        })

        self._uploadNext()

    def _uploadOk(self):
        self.results.append({
            'status' : 'OK',
            'msg': 'Successfully uploaded'
        })

        self._uploadNext()

    def _checkUpload(self):

        if self._aborted:
            return

        log.debug('Sending upload status request (%s)', self.upload_id)
        url = QUrl(self.UPLOAD_STATUS.format(id=self.upload_id))
        url.addQueryItem('token', self.auth_token)

        req = QNetworkRequest(url)

        self.reply = self.network_manager.get(req)

        self.reply.finished.connect(self._onUploadStatus)




    def _onUploadStatus(self):

        data = self._loadJson(str(self.reply.readAll()))

        self.reply = None

        if data is None:
            log.debug('Upload status failed (response: %s)', data)
            self._uploadFailed('Unknown error')
        elif 'upload_error' in data:
            log.debug('Upload status failed (%s)', data['upload_error'])
            self.statusMessage.emit('Upload failed')
            self._uploadFailed(data['upload_error'])
        else:
            self.statusMessage.emit(data['upload_status'])
            log.debug('Upload status %d (%s)', self.upload_id, data['upload_progress'])
            progress = int(data['upload_progress'])
            if progress == 0:
                progress = 10 # Just add a little to the progress so it doesn't look stuck
            self.itemProgress.emit(progress)
            if progress == 100:
                self._uploadOk()
            else:
                QTimer.singleShot(2500, self._checkUpload)




    def _loadJson(self, data):

        try:
            return json.loads(data)
        except ValueError, e:
            return None






