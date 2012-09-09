

import datetime

from xml.etree import cElementTree as ElementTree


class BrytonGPX(object):

    NAMESPACE = 'http://www.brytonsport.com/BDX/2/2'

    def __init__(self, xml, original):

        self._xml = xml
        self._original = original

    def _ns(self, path):
        return path.replace('NS-', "{%s}" % self.NAMESPACE)


    def getName(self):
        e = self._xml.find(self._ns('NS-metadata/NS-name'))
        if e is not None:
            return e.text


    def toString(self, pretty=True):

        return self._original



    def getSummary(self):

        ret = {}
        _ns = self._ns

        sum = self._xml.find(_ns('NS-extensions/NS-laps/NS-summary'))


        ret['start'] = sum.get('start')
        ret['end'] = sum.get('end')

        total_time = \
            datetime.datetime.strptime(ret['end'], '%Y-%m-%dT%H:%M:%SZ') \
            - \
            datetime.datetime.strptime(ret['start'], '%Y-%m-%dT%H:%M:%SZ')

        ret['total_time'] = total_time.seconds


        ret['distance'] = float(sum.find(_ns('NS-distance')).text)
        ret['calories'] = int(sum.find(_ns('NS-calorie')).text)
        ret['altloss'] = float(sum.find(_ns('NS-altloss')).text)
        ret['altgain'] = float(sum.find(_ns('NS-altgain')).text)



        speed = sum.find(_ns('NS-speed'))
        if float(speed.get('max')) > 0:
            ret['speed_avg'] = float(speed.get('avg', 0))
            ret['speed_max'] = float(speed.get('max', 0))

        hr = sum.find(_ns('NS-hrm'))
        if int(hr.get('max')) > 0:
            ret['hr_avg'] = int(hr.get('avg', 0))
            ret['hr_max'] = int(hr.get('max', 0))

        cad = sum.find(_ns('NS-cad'))
        if int(cad.get('max')) > 0:
            ret['cad_avg'] = int(cad.get('avg', 0))
            ret['cad_max'] = int(cad.get('max', 0))

        pwr = sum.find(_ns('NS-pwr'))
        if int(pwr.get('max')) > 0:
            ret['pwr_avg'] = int(pwr.get('avg', 0))
            ret['pwr_max'] = int(pwr.get('max', 0))

        ret['ride_time'] = int(sum.find(_ns('NS-rtime')).text)

        return ret

    def getLaps(self):
        return self.getTrackPoints()

    def getTrackPoints(self):

        laps = []
        _ns = self._ns

        track_segs = self._xml.findall(_ns('NS-trk/NS-trkseg'))
        log_segs = self._xml.findall(_ns('NS-extensions/NS-ssrlog/NS-logseg'))
        recorded_laps = self._getLaps()

        lap = []

        for track_seg, log_seg in zip(track_segs, log_segs):

            track_points = track_seg.findall(_ns('NS-trkpt'))
            log_points = log_seg.findall(_ns('NS-logpt'))



            if len(track_points) == 0:
                # If there are no track points we just skip to the next track segment
                # This happens when the track is paused.
                # Add None to indicate pause.

                # Sometimes it can be multiple segments without track point
                # We add only one None
                if lap and lap[-1] is not None:
                    lap.append(None)
                continue


            while track_points or log_points:

                point = {}

                track_point, log_point = self._getPoints(track_points, log_points)

                if track_point is not None:
                    p = track_point
                    point['lat'] = float(p.get('lat'))
                    point['lon'] = float(p.get('lon'))
                    point['ele'] = float(p.find(_ns('NS-ele')).text)
                    point['time'] = p.find(_ns('NS-time')).text


                if log_point is not None:

                    p = log_point

                    point['time'] = p.get('time')

                    spd = p.find(_ns('NS-spd'))
                    if spd is not None:
                        point['spd'] = float(spd.text)

                    tmp = p.find(_ns('NS-tmp'))
                    if tmp is not None:
                        point['tmp'] = float(tmp.text)

                    brm = p.find(_ns('NS-brm'))
                    if brm is not None:
                        point['brm'] = float(brm.text)

                    hrm = p.find(_ns('NS-hrm'))
                    if hrm is not None:
                        point['hrm'] = int(float(hrm.text))

                    cad = p.find(_ns('NS-cad'))
                    if cad is not None:
                        point['cad'] = int(cad.text)

                    pwr = p.find(_ns('NS-pwr'))
                    if pwr is not None:
                        point['pwr'] = int(pwr.text)


                if recorded_laps and recorded_laps[0]['end'] < point['time']:
                    rec_lap = recorded_laps.pop(0)
                    rec_lap['track_points'] = lap
                    laps.append(rec_lap)
                    lap = []

                lap.append(point)


            # Add None to indicate that the track was paused
            # if this is the last track segment, the None will be removed
            # below.
            lap.append(None)


        if lap:
            lap.pop() # remove last None


        if len(laps) > 0 and lap:

            laps.append(self._generateLastLap(laps, lap))
        elif lap:
            l = self.getSummary()
            l['track_points'] = lap

            laps.append(l)


        for lap in laps:
            self._mergePoints(lap)



        return laps


    def _mergePoints(self, lap):
        """
        The track points and log points doesn't allways happend at the same time
        and there is also usually more track points than log points.
        This function merges some of  the track points with the next log point.
        """


        last_track_point = None

        ret = []
        for p in lap['track_points']:
            if p is None:
                # Pause
                ret.append(p)
                continue

            if 'lat' in p and 'spd' in p:
                # We have a track point and a log point
                ret.append(p)
                last_track_point = None
            elif 'lat' in p:
                # Only a track point
                # save this for later so we can merge this with the
                # next log point
                last_track_point = p
                ret.append(p)
            elif last_track_point is None:
                # There was no track point so we just add this
                # log point without a track point
                ret.append(p)
            else:
                del p['time'] #Del time so the time from the track point is used
                # merge with last track_point
                last_track_point.update(p)
                last_track_point = None

        lap['track_points'] = ret


    def _generateLastLap(self, laps, rest_points):

        sum = self.getSummary()

        dist = sum['distance']
        cal = sum['calories']
        ride_time = sum['ride_time']
        for l in laps:
            dist -= l['distance']
            cal -= l['calories']
            ride_time -= l['ride_time']

        lap = {
            'distance' : dist,
            'start' : laps[-1]['end'],
            'end' : sum['end'],
            'calories' : cal,
            'ride_time' : ride_time,
        }

        total_time = \
            datetime.datetime.strptime(lap['end'], '%Y-%m-%dT%H:%M:%SZ') \
            - \
            datetime.datetime.strptime(lap['start'], '%Y-%m-%dT%H:%M:%SZ')

        lap['total_time'] = total_time.seconds


        spd = [0.0, 0.0, 0.0]
        hr = [0, 0, 0]
        pwr = [0, 0, 0]
        # last_spd = 0.0
        for p in rest_points:

            if 'spd' in p:
                spd[0] += p['spd']
                spd[1] += 1

                if p['spd'] > spd[2]:
                    spd[2] = p['spd']

            #     last_spd = p['spd']
            # else:
            #     spd[0] += last_spd
            #     spd[1] += 1


            if 'hrm' in p:
                hr[0] += p['hrm']
                hr[1] += 1
                if p['hrm'] > hr[2]:
                    hr[2] = p['hrm']

            if 'pwr' in p:
                pwr[0] += p['pwr']
                pwr[1] += 1
                if p['pwr'] > pwr[2]:
                    pwr[2] = p['pwr']



        if spd[0] > 0:
            lap['speed_max'] = spd[2]
            # lap['speed_avg'] = spd[0] / spd[1]
            lap['speed_avg'] = float(dist) / ride_time * 60 * 60 / 1000

        if hr[0] > 0:
            lap['hr_max'] = hr[2]
            lap['hr_avg'] = int(float(hr[0]) / hr[1])


        if pwr[0] > 0:
            lap['pwr_max'] = pwr[2]
            lap['pwr_avg'] = int(float(pwr[0]) / pwr[1])


        lap['track_points'] = rest_points

        return lap

    def _getLaps(self):

        laps = []
        _ns = self._ns

        for lap in self._xml.findall(_ns('NS-extensions/NS-laps/NS-lap')):

            l = {
                'start' : lap.get('start'),
                'end' : lap.get('end'),
                'calories' : int(lap.find(_ns('NS-calorie')).text),
                'distance' : float(lap.find(_ns('NS-distance')).text)
            }


            total_time = \
                datetime.datetime.strptime(l['end'], '%Y-%m-%dT%H:%M:%SZ') \
                - \
                datetime.datetime.strptime(l['start'], '%Y-%m-%dT%H:%M:%SZ')

            l['total_time'] = total_time.seconds

            speed = lap.find(_ns('NS-speed'))

            if float(speed.get('max')) > 0:
                l['speed_max'] = float(speed.get('max'))
                l['speed_avg'] = float(speed.get('avg'))

            hrm = lap.find(_ns('NS-hrm'))

            if int(hrm.get('max')) > 0:
                l['hr_max'] = int(hrm.get('max'))
                l['hr_avg'] = int(hrm.get('avg'))

            cad = lap.find(_ns('NS-cad'))

            if int(cad.get('max')) > 0:
                l['cad_max'] = int(cad.get('max'))
                l['cad_avg'] = int(cad.get('avg'))

            pwr = lap.find(_ns('NS-pwr'))

            if int(pwr.get('max')) > 0:
                l['pwr_max'] = int(pwr.get('max'))
                l['pwr_avg'] = int(pwr.get('avg'))

            l['ride_time'] = int(lap.find(_ns('NS-rtime')).text)

            laps.append(l)


        return laps



    def _getPoints(self, track_points, log_points):


        t_time = track_points[0].find(self._ns('NS-time')).text if track_points else None
        l_time = log_points[0].get('time') if log_points else None

        if t_time == l_time:
            return track_points.pop(0), log_points.pop(0)
        elif l_time is None or (t_time is not None and t_time < l_time):
            return track_points.pop(0), None
        else:
            return None, log_points.pop(0)










def bryton_gpx_from_string(gpx_data):
    xml = ElementTree.fromstring(gpx_data)
    return BrytonGPX(xml, gpx_data)
def bryton_gpx_from_file(gpx_file):
    xml = ElementTree.parse(gpx_file)
    return BrytonGPX(xml, open(gpx_file).read())




