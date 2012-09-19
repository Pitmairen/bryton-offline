
import socket
import errno
import os
import re
import logging

from wsgiref.simple_server import make_server
from zipfile import ZipFile
from cStringIO import StringIO
from xml.etree import cElementTree as ElementTree

from PyQt4.QtCore import QThread, pyqtSignal

from webob import Request, Response
from webob.exc import HTTPNotFound, HTTPForbidden


from gpx import bryton_gpx_from_string


log = logging.getLogger(__name__)


DATA = []

def parse_track_list(data):

    log.debug('Parsing track list')
    xml = ElementTree.parse(StringIO(data))

    ret = []


    for rec in xml.findall('Track/record'):

        id = rec.get('id')
        name = rec.find('name')
        if id is not None and name is not None:
            ret.append({
                'id' : id,
                'name' : name.text,
            })


    log.debug(ret)
    return ret





def upload_track_list(req):

    log.debug('Receving track list request')

    if req.method == 'POST':

        tracks = parse_track_list(req.POST.items()[0][0]+'='+req.POST.items()[0][1])

        DATA.append(('track_list', tracks))

    return 'ok'


_filename_re = re.compile(r'\d{9,}\.gpx')

def upload_track_data(req):


    log.debug('Receving track data request')

    f = req.POST['filename']

    data = []

    with ZipFile(f.file) as zf:

        for name in zf.namelist():
            log.debug('Filename: %s', name)
            if _filename_re.match(name):
                log.debug('Matched re %s', name)
                with zf.open(name) as gpxf:

                    data.append({
                        'name' : name,
                        'data' : gpxf.read()})


    DATA.append(('track_data', data))

    log.debug('Uploaded data track count %s', len(data))

    return 'ok'



class App(object):

    def __init__(self, session_id):
        self.session_id = session_id

        self.views = {
            '/track_list' : upload_track_list,
            '/track_data' : upload_track_data,
        }

    def __call__(self, environ, start_response):


        request = Request(environ)


        if request.headers.get('Sessionid') != self.session_id:
            log.debug('Request with invalid session_id')
            response = HTTPForbidden('Authentication Failed')
        else:

            path = request.path_info

            if path in self.views:
                response = Response(self.views[path](request))
            else:
                log.debug('Request with invalid path')
                response = HTTPNotFound('Not Found')




        return response(environ, start_response)



class TracksParser(object):


    def __init__(self, track_list, track_data):
        self._tracks = track_list
        self._data = track_data



    def getTracks(self):
        self._processData()
        return self._tracks




    def _processData(self):
        self._parseXML()
        self._matchTracks()





    def _matchTracks(self):

        log.debug('Matching track list with track data')
        for track in self._tracks:

            filename = track['name'].replace('/', '') \
                    .replace(' ', '') \
                    .replace(':', '') + '0.gpx'

            track['gpx'] = None

            for data in self._data:

                if 'match' in data and data['match']:
                    continue
                log.debug('%s - %s', filename, data['name'])
                if filename == data['name']:
                    track['gpx'] = data['data']
                elif self._matchTrack(track['name'], data['data']):
                    track['gpx'] = data['data']
                elif (track['id']+'.gpx') == ('T'+data['name']):
                    track['gpx'] = data['data']

                if track['gpx'] is not None:
                    log.debug('Found match')
                    data['match'] = True
                    break

            if track['gpx'] is None:
                log.debug('No match found')
                raise ValueError('Invalid track data received')

        del self._data

    def _matchTrack(self, name, gpx):

        n = gpx.getName()

        return n is not None and n == name

    def _parseXML(self):
        for d in self._data:
            d['data'] = bryton_gpx_from_string(d['data'])



def process_track_data(track_list, track_data):

    data = TracksParser(track_list, track_data)

    return data.getTracks()





class ServerThread(QThread):


    trackListUploaded = pyqtSignal(int)
    trackDataUploaded = pyqtSignal()
    trackListReady = pyqtSignal(list)
    error = pyqtSignal(str)

    serverStarted = pyqtSignal(int)

    def __init__(self, host, port, parent=None):
        self.host = host
        self.port = port

        self.session_id = os.urandom(10).encode('hex')

        super(ServerThread, self).__init__(parent)



    def make_server(self):

        port = self.port
        app = App(self.session_id)
        while True:

            try:
                httpd = make_server(self.host, port, app)
                break
            except socket.error, e:

                if e.errno == errno.EADDRINUSE and port < (self.port + 10):
                    port += 1
                else:
                    log.debug('Failed to create server')
                    self.serverError.emit('Failed to create server')
                    return False

        self.serverStarted.emit(port)

        self.httpd = httpd

        return True


    def run(self):

        if not self.make_server():
            return

        track_data = []

        while True:
            self.httpd.handle_request()

            if DATA:

                value = DATA.pop(0)

                if value[0] == 'track_list':
                    self.trackListUploaded.emit(len(value[1]))
                    if len(value[1]) > 0:
                        track_data.append(value[1])
                elif value[0] == 'track_data':
                    self.trackDataUploaded.emit()
                    track_data.append(value[1])


            if len(track_data) == 2:

                track_list = track_data.pop(0)
                list_data = track_data.pop(0)
                try:
                    tracks = process_track_data(track_list, list_data)
                    self.trackListReady.emit(tracks)
                except Exception, e:
                    log.debug('Failed to parse uploaded tracks')
                    self.error.emit('Failed to parse uploaded tracks')


