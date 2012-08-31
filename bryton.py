
import logging


from PyQt4.QtCore import (
    QObject, pyqtSignal, QTimer
)
from PyQt4.QtNetwork import QTcpSocket


from server import ServerThread



log = logging.getLogger(__name__)



CONNECTING = 0
REFRESH_TRACKLIST = 1
WAITING_TRACKLIST = 2
WAITING_TRACKDATA = 3
IDLE = 4
UPLOAD_BRYTONSPORT = 5
DELETE_TRACKS = 6
FINALIZING = 7



class BrytonClient(QObject):

    connected = pyqtSignal()
    deviceReady = pyqtSignal()
    deviceOffline = pyqtSignal()
    error = pyqtSignal(str)
    BBVersion = pyqtSignal(str)

    refreshingTrackList = pyqtSignal()
    trackListProgress = pyqtSignal(str)
    trackListReady = pyqtSignal()

    statusMessage = pyqtSignal(str)


    uploadFinished = pyqtSignal()
    uploadFailed = pyqtSignal()
    uploadProgress = pyqtSignal(int)


    finalizingProgress = pyqtSignal(int)
    tracksDeleted = pyqtSignal()
    deleteFailed = pyqtSignal()


    def __init__(self, host='localhost', port_range=range(6776, 6781),
            server_host='localhost', server_port=24011, parent=None):
        super(BrytonClient, self).__init__(parent)

        self._host = host
        self._port = port_range[0]
        self._port_range = port_range

        self._server_port = None
        self._server_host = server_host

        self._socket = s = QTcpSocket(self)

        s.readyRead.connect(self._onReadyRead)
        s.connected.connect(self._onConnected)
        s.disconnected.connect(self._onDisconnected)
        s.error.connect(self._onSocketError)


        self.connected.connect(self._getState)
        self.deviceReady.connect(self._refreshTrackList)

        self.server = ServerThread('', server_port, self)

        self.server.trackListUploaded.connect(self._onTrackListUploaded)
        self.server.trackDataUploaded.connect(self._onTrackDataUploaded)
        self.server.trackListReady.connect(self._onTracksUploaded)
        self.server.error.connect(self._onError)
        self.server.serverStarted.connect(self._onServerStarted)


        self.reset()

        self.server.start()


    def reset(self):
        self._last_req_id = 1
        self._cid = None
        self._req_is_ack = False
        self._deviceReady = False
        self._current_status = 'connecting'
        self._state = CONNECTING
        self._track_count = 0
        self._started = False
        self._aborted_by_error = False
        self._req_state_on_ack = False
        self._port = self._port_range[0]
        self._socket.abort()


    def is_connected(self):
        return self._cid is not None

    def is_server_started(self):
        return self._server_port is not None

    def start(self):
        self._started = True
        # If the server has not yet started we wait until the server has
        # been started before we start the client.
        if self.is_server_started():
            self._doStart()
        else:
            self.statusMessage.emit('Starting internal server')


    def uploadToBrytonSport(self, session_id):
        self._state = UPLOAD_BRYTONSPORT
        self._writeRequest('$GetDevDataAll', data=[session_id,
            '"http://api.brytonsport.com/storages/put"'])
        # QTimer.singleShot(1500, self._getReqState)
        self._req_state_on_ack = True


    def deleteTracks(self, track_ids):
        self._state = DELETE_TRACKS
        self._writeRequest('$DelDevData', data=[self.server.session_id, "{}".format(','.join(track_ids))])
        self._req_state_on_ack = True


    def _doStart(self):
        log.debug('Starting client')
        self.statusMessage.emit('Connecting to BrytonBridge')
        self._connect()

    def _onServerStarted(self, port):
        log.debug('Internal server started')
        self._server_port = port
        self._server_addr = 'http://{0}:{1}'.format(self._server_host, self._server_port)

        if self._started:
            self._doStart()


    def _onTrackListUploaded(self, track_count):
        self._track_count = track_count
        self.trackListProgress.emit('loading track data')


    def _onTrackDataUploaded(self):
        self.trackListProgress.emit('processing track data')


    def _onTracksUploaded(self, track_list):
        self.track_list = track_list
        self.trackListReady.emit()


    def _onReadyRead(self):

        while self._socket.canReadLine():

            line = str(self._socket.readLine()).rstrip()
            log.debug('readLine, %s', line)
            self._parseResponse(line)


    def _onConnected(self):
        log.debug('Connected')
        self._writeLine(['$Connect', '1'])

        def _connectionTimeoutTest():
            if not self.is_connected() and not self._aborted_by_error:
                log.debug('No response from $Connect, aborting.')
                # if we are not connected by the time we get here
                # we try the next port.
                # this can happen if another server is running on the port and let
                # us connect, but does not respond to the $Connect command
                self._socket.abort()
                self._connect(1)

        QTimer.singleShot(2000, _connectionTimeoutTest)


    def _onDisconnected(self):
        log.debug('Disconnected')
        if self.is_connected() and not self._aborted_by_error:
            self._onError('Lost connection to BrytonBridge')


    def _onSocketError(self, code):
        if code == QTcpSocket.ConnectionRefusedError:
            log.debug('Connection refused')
            # Try the next port
            self._connect(1)
        else:
            log.debug('Socket error "%s"', self._socket.errorString())
            self._onError(self._socket.errorString())


    def _onError(self, msg):
        log.debug('Error "%s"', msg)
        self._aborted_by_error = True
        self._socket.abort()
        self.error.emit(msg)


    def _refreshTrackList(self):
        self.refreshingTrackList.emit()
        self._current_status = 'refresh-tracklist'
        self._state = REFRESH_TRACKLIST
        self._track_count = None
        self._getState()


    def _getState(self):
        self._writeRequest('$GetState')


    def _getReqState(self):
        self._writeRequest('$GetState', req_id=self._last_req_id)


    def _getDevState(self):
        self._writeRequest('$GetDevState')


    def _getDevDataList(self):
        self._writeRequest('$GetDevDataList', data=[self.server.session_id,
            '"{0}/{1}"'.format(self._server_addr, 'track_list')])
        self._req_state_on_ack = True


    def _getDevDataAll(self):
        self._writeRequest('$GetDevDataAll', data=[self.server.session_id,
            '"{0}/{1}"'.format(self._server_addr, 'track_data')])
        self._req_state_on_ack = True


    def _finalize(self):
        log.debug('Finalizing')
        self._state = FINALIZING
        self._writeRequest('$Finalize')
        self._req_state_on_ack = True

    def _writeRequest(self, cmd, data=None, req_id=None):

        self._req_is_ack = False

        if req_id is None:
            req_id = self._nextReqId()

        req = [cmd, req_id, self._last_resp_id]

        if self.is_connected():
            req.append(self._cid)

        if data is not None:
            req.extend(data)

        self._writeLine(req)


    def _writeLine(self, cmd):
        log.debug('writeLine, %s', ','.join(map(str, cmd)))
        self._socket.write(','.join(map(str, cmd))+'\r\n')


    def _writeACK(self, resp_id):
        self._last_resp_id = resp_id
        self._writeLine(['$ACK', resp_id, self._cid])



    def _parseResponse(self, resp):

        cmd, rest = resp.split(',', 1)

        if cmd == '$NAK':
            self._parseNAK(rest)
        elif not self.is_connected():
            if not self._last_req_confirmed():
                self._parseACK(cmd, rest)
            elif cmd == '$CID':
                self._parseCID(rest)
            else:
                self._onError('Unexpected Response')

        elif cmd == '$DevState':
            # DevState can be sendt without being requested when
            # the device is pluggen in or out while connected to
            # BrytonBridge
            self._parseDevState(rest)
        elif not self._last_req_confirmed():
            self._parseACK(cmd, rest)
        elif cmd == '$State':
            self._parseState(rest)
        else:
            self._onError('Unexpected Response')



    def _parseACK(self, cmd, resp):

        if cmd != '$ACK':
            self._onError('Unexpected Response')
            return

        if not self.is_connected():
            if resp == '1':
                self._set_req_confirmed()
        else:
            req_id, cid = resp.split(',')

            if self._validateResponse(req_id, cid):
                self._set_req_confirmed()

                if self._req_state_on_ack:
                    self._req_state_on_ack = False
                    QTimer.singleShot(1000, self._getReqState)




    def _parseCID(self, resp):

        resp_id, req_id, cid = resp.split(',')

        if req_id != str(self._last_req_id):
            self._onError('Unexpected Response')
            return
        self._cid = cid
        self._writeACK(resp_id)

        self.connected.emit()

    def _parseNAK(self, resp):
        msg = resp.split(',')[-1]

        if msg == 'undefined':
            msg = 'Unknown error response from BrytonBridge'
        elif msg == 'NOT SUPPORT MULTI CONNECTION':
            msg = 'You can only have one connection to BrytonBridge open.'\
                  ' If you have your web browser opened at brytonsport.com please'\
                  ' close the browser and retry.'
        self._onError(msg)


    def _parseDevState(self, resp):
        resp_id, _, _, name, rev, firmware, _, serial, size, used, state = resp.split(',')

        self.dev_state = state = {
            'name' : name,
            'rev' : rev, #Not sure what this value is
            'firmware' : firmware,
            'serial' : serial,
            'total_storage' : int(size),
            'storage_used' : int(used),
            'state' : state,
        }

        self._writeACK(resp_id)


        if state['state'] == 'READY' and not self._deviceReady:
            self._deviceReady = True
            self.deviceReady.emit()
        elif state['state'] == 'OFFLINE':
            self._deviceReady = False
            self.deviceOffline.emit()


    def _parseState(self, resp):
        resp_id, req_id, cid, bb_version, status, progress, _ = resp.split(',')

        if not self._validateResponse(req_id, cid):
            return

        if self._current_status == 'connecting':
            self.BBVersion.emit(bb_version)
        self.state = state = {
            'req_id' : int(req_id),
            'bb_version' : bb_version,
            'state' : status,
            'progress' : progress,
        }

        self._writeACK(resp_id)



        if state['progress'] == 'ERROR':
            msg = 'Request failed'

            if self._state == UPLOAD_BRYTONSPORT:
                log.debug('Upload failed')
                self._brytonSportUploadFailed()
                return
            elif self._state in (FINALIZING, DELETE_TRACKS):
                log.debug('Delete Failed')
                self._state = IDLE
                self.deleteFailed.emit()
                return

            elif self._state in (REFRESH_TRACKLIST, WAITING_TRACKDATA, WAITING_TRACKDATA):
                msg = '''Request failed. Make sure the hostname of the internal server is correct.'''

            self._onError(msg)

            return


        state['progress'] = float(state['progress'])
        if state['state'] == 'READY':

            if self._state == CONNECTING:
                self._getDevState()
            elif self._state == REFRESH_TRACKLIST:
                self._state = WAITING_TRACKLIST
                self._getDevDataList()
                # QTimer.singleShot(1000, self._getReqState)

            elif self._state == WAITING_TRACKLIST:

                if self._track_count is None:
                    # Bryton bridge is finished sending the data, but the server
                    # thread is not yet finished processing the data, so we wait.
                    QTimer.singleShot(1000, self._getReqState)
                    return
                elif self._track_count == 0:
                    self._current_status = ''
                    self._onTracksUploaded([])
                    return

                self._getDevDataAll()
                self._state = WAITING_TRACKDATA
                # QTimer.singleShot(1000, self._getReqState)

            elif self._state == WAITING_TRACKDATA:
                self._state = IDLE

            elif self._state == UPLOAD_BRYTONSPORT:
                self._state = IDLE
                self.uploadFinished.emit()
                log.debug('Upload finished')
            elif self._state == DELETE_TRACKS:
                self._state = IDLE
                self._finalize()
            elif self._state == FINALIZING:
                log.debug('Finalize complete')
                self._state = IDLE
                self.tracksDeleted.emit()
                self._refreshTrackList()

        elif state['state'] == 'PROGRESSING':

            QTimer.singleShot(2000, self._getReqState)
            if self._state == UPLOAD_BRYTONSPORT:
                log.debug('Upload progress %f', state['progress'])
                self.uploadProgress.emit(state['progress']*100)

            elif self._state == FINALIZING:
                log.debug('Finalize progress %f', state['progress'])
                self.finalizingProgress.emit(state['progress']*100)


    def _connect(self, incr_port=0):
        port = self._port + incr_port
        if port in self._port_range:
            self._port = port
            self._socket.connectToHost(self._host, port)
        else:
            self._onError('Could not connect to BrytonBridge')



    def _validateResponse(self, req_id, cid):

        if req_id != str(self._last_req_id) or cid != self._cid:
            self._onError('Unexpected response from BrytonBridge')
            return False
        return True

    def _brytonSportUploadFailed(self):
        self._state = IDLE
        self.uploadFailed.emit()

    def _nextReqId(self):
        self._last_req_id += 1
        return self._last_req_id


    def _last_req_confirmed(self):
        return self._req_is_ack


    def _set_req_confirmed(self):
        self._req_is_ack = True








