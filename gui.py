

import datetime
from os import path


from PyQt4.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt4.QtGui import (
    QWidget, QTabWidget, QListWidget, QLabel, QGroupBox, QPixmap,
    QProgressBar, QFrame, QListWidgetItem, QIcon, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog, QMenu,
    QComboBox,
)



import strava
import tcx
import brytonsport

from busy import MessageWidget
from bryton import BrytonClient
from utils import ProgressDialog


#BrytonBridge versions
TESTED_VERSIONS = ['2.2.0.36']


TRACK_ITEM_ROLE = Qt.UserRole + 1

class MainWindow(QWidget):


    def __init__(self, config, parent=None):
        super(MainWindow, self).__init__(parent)

        self.bbclient = BrytonClient(parent=self,
                server_host=config.get('server_host'))

        self.history_list_widget = HistoryWidget(self.bbclient, config, self)
        self.device_info_widget = DeviceInfoWidget(self)
        self.track_summary_widget = TrackSummaryWidget(self)


        self.track_tabs = QTabWidget(self)

        self.track_tabs.setMaximumWidth(200)

        self.track_tabs.addTab(self.history_list_widget, 'History')


        self.history_list_widget.currentTrackChanged.connect(self._onHistoryTrackChanged)


        self.bb_version = QLabel('', self)
        self.bb_version.setAlignment(Qt.AlignRight)
        self.bb_version.setContentsMargins(0, 0, 3, 0)

        self._createLayout()

        self.message_overlay = MessageWidget(self)
        self.message_overlay.setLoading('Connecting to BrytonBridge')

        self.message_overlay.retryClicked.connect(self._onRetry)



        self.bbclient.statusMessage.connect(self.message_overlay.setLoading)

        self.bbclient.connected.connect(self._onConnected)
        self.bbclient.deviceOffline.connect(self._onDeviceOffline)
        self.bbclient.deviceReady.connect(self._onDeviceReady)
        self.bbclient.trackListReady.connect(self._onTrackListReady)
        self.bbclient.error.connect(self._onError)
        self.bbclient.BBVersion.connect(self._onBBVersion)
        self.bbclient.start()

        # self.message_overlay.hide()


    def _onConnected(self):
        self.message_overlay.setMessage('Searching for device')

    def _onDeviceReady(self):
        self.device_info_widget.setDeviceInfo(self.bbclient.dev_state)
        self.message_overlay.hide()

    def _onDeviceOffline(self):
        self.message_overlay.setDisconnected('Please connect your device')
        self.message_overlay.show()

    def _onError(self, msg):
        self.message_overlay.setError(msg)
        self.message_overlay.retry.show()
        self.message_overlay.show()

    def _onRetry(self):
        self.message_overlay.retry.hide()
        self.bbclient.reset()
        self.bbclient.start()

    def _onBBVersion(self, version):
        if version in TESTED_VERSIONS:
            self.bb_version.hide()
            self.bb_version.setText('BrytonBridge version <font color="green">{}</font>'.format(version))
        else:
            self.bb_version.show()
            self.bb_version.setText('BrytonBridge version <font color="red"><b>{}</b></font>'.format(version))
            self.bb_version.setToolTip('You are using an untested version of BrytonBridge')


    def _onTrackListReady(self):
        self.tracks = tracks = self.bbclient.track_list

        self.history_list_widget.setTrackList(tracks, self.bbclient.dev_state)

    def _onHistoryTrackChanged(self, track):

        self.track_summary_widget.setTrack(track)


    def resizeEvent(self, event):

        self.message_overlay.resize(event.size())

        super(MainWindow, self).resizeEvent(event)

    def _createLayout(self):

        la = QVBoxLayout()


        la.addWidget(self.bb_version)


        l = QHBoxLayout()

        l.addWidget(self.track_tabs, 0)

        v = QVBoxLayout()


        group = QGroupBox('Device', self)
        l2 = QHBoxLayout()
        l2.addWidget(self.device_info_widget)
        group.setLayout(l2)


        v.addWidget(group)


        group = QGroupBox('Track Summary', self)
        l2 = QHBoxLayout()
        l2.addWidget(self.track_summary_widget)
        group.setLayout(l2)


        v.addWidget(group, 1)


        l.addLayout(v, 1)


        la.addLayout(l)

        self.setLayout(la)





class HistoryWidget(QWidget):

    currentTrackChanged = pyqtSignal(dict)

    def __init__(self, bbclient, config, parent=None):
        super(HistoryWidget, self).__init__(parent)

        self.bbclient = bbclient
        self.config = config

        self.track_list = []

        self.list = QListWidget(self)
        self.list.setUniformItemSizes(True)
        self.list.setSelectionMode(QListWidget.ExtendedSelection)

        self.list.currentRowChanged.connect(self._onRowChanged)


        self.delete_btn = QPushButton(QIcon('img/delete.png'), '', self)
        self.save_btn = QPushButton(QIcon('img/save.png'), '', self)
        self.upload_btn = QPushButton(QIcon('img/upload.png'), '', self)

        for i, w in enumerate((self.delete_btn, self.save_btn, self.upload_btn)):
            w.setIconSize(QSize(22, 22))

            if i < 1:
                w.setMinimumSize(32, 32)
                w.setMaximumSize(32, 32)
            else:
                w.setMinimumSize(58, 32)
                w.setMaximumSize(58, 32)

        save_menu = QMenu('Export tracks', self)
        act = save_menu.addAction('Save as TCX')
        act.triggered.connect(self._onSaveAsTCX)
        act = save_menu.addAction('Save as BDX (Bryton GPX extension)')
        act.triggered.connect(self._onSaveAsBDX)

        self.save_btn.setMenu(save_menu)


        upload_menu = QMenu('Upload tracks', self)
        act = upload_menu.addAction(QIcon('img/strava-icon.png'), 'Upload to Strava.com')
        act.triggered.connect(self._onUploadStrava)
        act = upload_menu.addAction(QIcon('img/bryton-icon.png'), 'Upload to Brytonsport.com')
        act.triggered.connect(self._onUploadBrytonSport)


        self.upload_btn.setMenu(upload_menu)


        self.delete_btn.clicked.connect(self._onDeleteTracks)


        self._createLayout()


        self.message_overlay = MessageWidget(self)
        self.message_overlay.setLoading('Loading tracklist')


        bbclient.refreshingTrackList.connect(self.message_overlay.show)


    def setTrackList(self, track_list, device_info):

        self.list.clear()
        self.device_info = device_info
        self.track_list = track_list

        for track in track_list:

            item = QListWidgetItem(track['name'])
            item.setData(TRACK_ITEM_ROLE, track['id'])
            self.list.addItem(item)

        self.message_overlay.hide()


    def resizeEvent(self, event):

        self.message_overlay.resize(event.size())

        super(HistoryWidget, self).resizeEvent(event)


    def _onDeleteTracks(self):

        tracks = self._getSelectedTracks()

        if not tracks:
            tracks = self.track_list


        ids = map(lambda t: t['id'], tracks)
        names = map(lambda t: t['name'], tracks)

        msg = 'Are you sure you want to delete the following {} track(s):'.format(len(tracks))

        msg += '\n' + '\n'.join(names)


        res = QMessageBox.question(self, 'Delete tracks?',
                msg,
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

        print res

        if res == QMessageBox.Ok:
            print ids
            # self.bbclient._refreshTrackList()

            d = ProgressDialog('Finalizing', "Don't close this window\n(It may stall for a little while on 93%)", self)
            d.progress.setRange(0, 100)
            d.resize(250, 80)

            self.bbclient.finalizingProgress.connect(d.progress.setValue)
            self.bbclient.tracksDeleted.connect(d.accept)

            def _onFail():

                QMessageBox.warning(self, 'Delete failed')
                d.accept()

            self.bbclient.deleteFailed.connect(_onFail)

            self.bbclient.deleteTracks(ids)
            d.exec_()



    def _onUploadStrava(self):


        tracks = self._getSelectedTracks()

        if not tracks:
            tracks = self.track_list

        strava.upload_to_strava(tracks, self.device_info, self,
                auth_token=self.config.get('strava_auth_token'),
                password=self.config.get('strava_password'),
                username=self.config.get('strava_email'))


    def _onUploadBrytonSport(self):

        brytonsport.upload_to_brytonsport(self.bbclient, self,
                username=self.config.get('bryton_email'),
                password=self.config.get('bryton_password'),
                session_id=self.config.get('bryton_session_id'))

    def _onSaveAsTCX(self):

        tracks = self._getSelectedTracks()

        if not tracks:
            tracks = self.track_list
            # QMessageBox.information(self, 'No tracks selected', 'You need to select the tracks you want to save.')

        if not tracks:
            return

        if len(tracks) == 1:
            name = QFileDialog.getSaveFileName(self,
                'Save file %s' % tracks[0]['name'],
                self._trackFilename(tracks[0]['name'], 'tcx'),
                filter='TCX (*.tcx)')

            if name:

                self._saveContent(name, tcx.bryton_gpx_to_tcx(tracks[0]['gpx'], pretty=True, device=self.device_info))

        else:
            dir = QFileDialog.getExistingDirectory(self,
                'Open Directory', '', QFileDialog.ShowDirsOnly)

            if not dir:
                return
            for t in tracks:
                name = path.join(str(dir), self._trackFilename(t['name'], 'tcx'))
                self._saveContent(name, tcx.bryton_gpx_to_tcx(t['gpx'], pretty=True, device=self.device_info))




    def _onSaveAsBDX(self):
        tracks = self._getSelectedTracks()

        if not tracks:
            tracks = self.track_list

        if not tracks:
            return

        if len(tracks) == 1:
            name = QFileDialog.getSaveFileName(self,
                'Save file %s' % tracks[0]['name'],
                self._trackFilename(tracks[0]['name'], 'bdx'),
                filter='BDX (*.bdx)')

            if name:

                self._saveContent(name, tracks[0]['gpx'].toString(pretty=True))

        else:
            dir = QFileDialog.getExistingDirectory(self,
                'Open Directory', '', QFileDialog.ShowDirsOnly)

            if not dir:
                return
            for t in tracks:
                name = path.join(str(dir), self._trackFilename(t['name'], 'gpx'))
                self._saveContent(name, t['gpx'].toString(pretty=True))

    def _saveContent(self, filename, content):

        with open(filename, 'w') as f:
            f.write(content)


    def _trackFilename(self, name, ext):

        return name.replace('/', '').replace(' ', '-').replace(':', '') + '.' + ext



    def _getSelectedTracks(self):

        items = self.list.selectedItems()

        tracks = []

        for item in items:

            index = self.list.row(item)

            tracks.append(self.track_list[index])

        return tracks


    def _onRowChanged(self, row):

        track = self.track_list[row]

        self.currentTrackChanged.emit(track)


    def _createLayout(self):

        l = QVBoxLayout()

        l.addWidget(self.list)


        h = QHBoxLayout()

        h.addWidget(self.delete_btn)
        h.addStretch()
        h.addWidget(self.save_btn)
        h.addWidget(self.upload_btn)

        l.addLayout(h)

        self.setLayout(l)





class DeviceInfoWidget(QWidget):

    DEVICE_IMAGES = {
        'rider20' : 'img/rider20_icon.jpg',
        'rider30' : 'img/rider30_icon.jpg',
        'rider35' : 'img/rider35_icon.jpg',
        'rider40' : 'img/rider40_icon.jpg',
        'rider50' : 'img/rider40_icon.jpg',
        'rider' : 'img/rider_icon.jpg',
        'cardio30' : 'img/cardio30_icon.jpg',
        'cardio35' : 'img/cardio35_icon.jpg',
        'cardio' : 'img/cardio_icon.jpg',
    }


    def __init__(self, parent=None):
        super(DeviceInfoWidget, self).__init__(parent)

        self.image = QLabel(self)
        self.image.setPixmap(QPixmap(self.DEVICE_IMAGES['rider']))

        self.image_frame = QFrame(self)
        self.image_frame.setMaximumHeight(55)
        self.image_frame.setMinimumHeight(55)
        self.image_frame.setMaximumWidth(55)
        self.image_frame.setMinimumWidth(55)
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Raised)


        self.storage_usage = QProgressBar(self)
        self.storage_usage.setFormat('Disk usage %p%')
        self.storage_usage.setRange(0, 100)
        self.storage_usage.setValue(0)


        self.device_name = QLabel(self)
        self.device_name.setText('<b>Unknown</b>')
        self.device_name.setContentsMargins(3, 0, 0, 0)

        self._createLayout()


    def setDeviceInfo(self, dev_info):


        name = dev_info['name'].lower()

        if name in self.DEVICE_IMAGES:
            img = self.DEVICE_IMAGES[name]
        elif 'rider' in name:
            img = self.DEVICE_IMAGES['rider']
        elif 'cardio' in name:
            img = self.DEVICE_IMAGES['cardio']
        else:
            img = self.DEVICE_IMAGES['rider']

        self.device_name.setText('<b>%s</b>' % dev_info['name'])

        self.image.setPixmap(QPixmap(img))

        self.storage_usage.setValue(
            float(dev_info['storage_used']) / dev_info['total_storage'] * 100
        )





    def _createLayout(self):


        l = QHBoxLayout()
        l.addWidget(self.image)
        l.setContentsMargins(1, 1, 1, 1)

        self.image_frame.setLayout(l)

        l = QHBoxLayout()

        l.addWidget(self.image_frame)

        v = QVBoxLayout()

        v.addWidget(self.device_name)
        v.addWidget(self.storage_usage, 1)

        l.addLayout(v)

        self.setLayout(l)



class TrackSummaryWidget(QWidget):


    def __init__(self, parent=None):
        super(TrackSummaryWidget, self).__init__(parent)



        self.ride_time = QLabel(self)
        self.calories = QLabel(self)
        self.avg_speed = QLabel(self)
        self.max_speed = QLabel(self)
        self.avg_hr = QLabel(self)
        self.max_hr = QLabel(self)

        self.avg_cad = QLabel(self)
        self.max_cad = QLabel(self)

        self.avg_pwr = QLabel(self)
        self.max_pwr = QLabel(self)

        for l in self.children():
            if isinstance(l, QLabel):
                l.setTextInteractionFlags(Qt.TextSelectableByMouse)


        self.laps = QComboBox(self)
        self.laps.hide()


        self.laps.activated.connect(self._onLapChanged)


        self._createLayout()



    def setTrack(self, track):

        self.lap_summaries = laps = track['gpx'].getLaps()

        self.laps.clear()

        self.laps.addItem('Summary')
        for i, lap in enumerate(laps, 1):
            self.laps.addItem('Lap {0}'.format(i))

        if len(laps) > 1:
            self.laps.show()
        else:
            self.laps.hide()

        self.setTrackSummary(track['gpx'].getSummary())

        self.track = track

    def setTrackSummary(self, summary):

        ride_time = str(datetime.timedelta(seconds=summary['ride_time']))
        if len(ride_time) == 7:
            # Add 0 to get the format hh:mm::ss
            ride_time = '0' + ride_time

        self.ride_time.setText('<b>Ride time:</b><br> %s' % ride_time)

        dist = summary['distance'] / 1000.0

        self.calories.setText('<b>Distance:</b><br> %.2f Km' % dist)

        self.avg_speed.setText('<b>Avg Speed:</b><br> %.1f Km/h' % float(summary.get('speed_avg', 0)))
        self.max_speed.setText('<b>Max Speed:</b><br> %.1f Km/h' % float(summary.get('speed_max', 0)))


        self.avg_hr.setText('<b>Avg Heart rate:</b><br> %s bpm' % summary.get('hr_avg', '---'))
        self.max_hr.setText('<b>Max Heart rate:</b><br> %s bpm' % summary.get('hr_max', '---'))

        self.avg_cad.setText('<b>Avg Cadence:</b><br> %s rpm' % summary.get('cad_avg', '---'))
        self.max_cad.setText('<b>Max Cadence:</b><br> %s rpm' % summary.get('cad_max', '---'))

        self.avg_pwr.setText('<b>Avg Power:</b><br> %s watts' % summary.get('pwr_avg', '---'))
        self.max_pwr.setText('<b>Max Power:</b><br> %s watts' % summary.get('pwr_max', '---'))

    def _onLapChanged(self, i):

        if i == 0:
            self.setTrackSummary(self.track['gpx'].getSummary())
        else:
            self.setTrackSummary(self.lap_summaries[i-1])


    def _createLayout(self):

        l = QVBoxLayout()

        h = QHBoxLayout()

        v = QVBoxLayout()
        v.addWidget(self.ride_time)
        v.addWidget(self.avg_speed)
        v.addWidget(self.avg_hr)
        v.addWidget(self.avg_cad)
        v.addWidget(self.avg_pwr)

        h.addLayout(v)

        v = QVBoxLayout()
        v.addWidget(self.calories)
        v.addWidget(self.max_speed)
        v.addWidget(self.max_hr)
        v.addWidget(self.max_cad)
        v.addWidget(self.max_pwr)

        h.addLayout(v)


        l.addLayout(h)

        l.addSpacing(10)
        l.addWidget(self.laps)


        l.addStretch()


        self.setLayout(l)



