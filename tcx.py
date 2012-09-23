
import re

from xml.etree import cElementTree as xml

from version import VERSION
from utils import indent_element_tree



_DEFAULT_NS = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
_ACTIVITY_EXT_NS = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
_XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
def _activity_ext_ns(tag):

    return '{%s}%s' % (_ACTIVITY_EXT_NS, tag)

def _ns(tag):

    return '{%s}%s' % (_DEFAULT_NS, tag)

def _ns_xsi(tag):
    return '{%s}%s' % (_XSI_NS, tag)


def kph_to_ms(value):

    return value * 1000 / 3600


def bryton_gpx_to_tcx(gpx, activity_type='ride', device=None, pretty=False):


    root = xml.Element(_ns('TrainingCenterDatabase'))


    root.set(_ns_xsi('schemaLocation'),
        '''%s %s %s %s''' % (
        'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd',
        'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd',
        ))

    xml.register_namespace('a', _ACTIVITY_EXT_NS)
    xml.register_namespace('', _DEFAULT_NS)

    activities = xml.SubElement(root, _ns('Activities'))


    activity = xml.SubElement(activities, _ns('Activity'))


    if activity_type == 'ride':
        activity.set(_ns('Sport'), 'Biking')
    elif activity_type == 'run':
        activity.set(_ns('Sport'), 'Running')
    else:
        activity.set(_ns('Sport'), 'Other')

    id = xml.SubElement(activity, _ns('Id'))
    id.text = gpx.getSummary()['start']


    for lap in gpx.getTrackPoints():


        lap_el = xml.SubElement(activity, _ns('Lap'))

        lap_el.set(_ns('StartTime'), lap['start'])

        ride_time = xml.SubElement(lap_el, _ns('TotalTimeSeconds'))
        ride_time.text=str(float(lap['total_time']))

        dist = xml.SubElement(lap_el, _ns('DistanceMeters'))
        dist.text = str(float(lap['distance']))

        if 'speed_max' in lap:
            max_speed = xml.SubElement(lap_el, _ns('MaximumSpeed'))
            max_speed.text = str(kph_to_ms(float(lap['speed_max'])))

        cals = xml.SubElement(lap_el, _ns('Calories'))
        cals.text = str(lap['calories'])


        if 'hr_max' in lap:

            avg_hr = xml.SubElement(lap_el, _ns('AverageHeartRateBpm'))
            val = xml.SubElement(avg_hr, _ns('Value'))
            val.text = str(lap['hr_avg'])

            max_hr = xml.SubElement(lap_el, _ns('MaximumHeartRateBpm'))
            val = xml.SubElement(max_hr, _ns('Value'))
            val.text = str(lap['hr_max'])

        intensity = xml.SubElement(lap_el, _ns('Intensity'))
        intensity.text = 'Active'

        if activity_type == 'ride' and 'cad_avg' in lap:
            cadence = xml.SubElement(lap_el, _ns('Cadence'))
            cadence.text = str(lap['cad_avg'])


        trigger = xml.SubElement(lap_el, _ns('TriggerMethod'))
        trigger.text = 'Manual'



        track = xml.SubElement(lap_el, _ns('Track'))


        # dist = 0.0
        # prev = []
        for point in lap['track_points']:

            if point is None:
                # Track was paused
                track = xml.SubElement(lap_el, _ns('Track'))
                continue


            track_point = xml.SubElement(track, _ns('Trackpoint'))

            time = xml.SubElement(track_point, _ns('Time'))
            time.text = point['time']



            if 'lat' in point:
                pos = xml.SubElement(track_point, _ns('Position'))


                lat = xml.SubElement(pos, _ns('LatitudeDegrees'))
                lon = xml.SubElement(pos, _ns('LongitudeDegrees'))
                lat.text = str(point['lat'])
                lon.text = str(point['lon'])




            if 'ele' in point:

                alt = xml.SubElement(track_point, _ns('AltitudeMeters'))
                alt.text = str(float(point['ele']))


            # if 'lat' in point:
            #     import math
            #     from geopy import distance
            #     if len(prev) >= 2:
            #         # dist += round(geo_distance(prev['lat'], prev['lon'], point['lat'], point['lon']) * 1000.0, 3)

            #         dist += distance.distance('%s;%s' % (prev[0]['lat'], prev[0]['lon']), '%s;%s' % (point['lat'], point['lon'])).m
            #         prev.pop(0)
            #     elif len(prev) > 0:

            #         dist += distance.distance('%s;%s' % (prev[0]['lat'], prev[0]['lon']), '%s;%s' % (point['lat'], point['lon'])).m
            #     # dist = round(dist, 1)
            #     print math.floor(dist)

            #     dist_el = xml.SubElement(track_point, _ns('DistanceMeters'))
            #     dist_el.text = str(dist)

            #     prev.append(point)




            if 'hrm' in point:
                hr = xml.SubElement(track_point, _ns('HeartRateBpm'))

                val = xml.SubElement(hr, _ns('Value'))
                val.text = str(point['hrm'])

            if 'cad' in point and activity_type == 'ride':

                cad = xml.SubElement(track_point, _ns('Cadence'))
                cad.text = str(point['cad'])


            if 'spd' in point or 'pwr' in point or 'cad' in point:

                ext = xml.SubElement(track_point, _ns('Extensions'))

                tpx = xml.SubElement(ext, _activity_ext_ns('TPX'))


                if 'spd' in point:
                    speed = xml.SubElement(tpx, _activity_ext_ns('Speed'))

                    speed.text = str(kph_to_ms(point['spd']))

                if 'cad' in point and activity_type == 'run':
                    cad = xml.SubElement(tpx, _activity_ext_ns('RunCadence'))
                    cad.text = str(point['cad'])

                if 'pwr' in point:

                    pwr = xml.SubElement(tpx, _activity_ext_ns('Watts'))

                    pwr.text = str(point['pwr'])



        if 'speed_avg' in lap or 'cad_max' in lap:
            ext = xml.SubElement(lap_el, _ns('Extensions'))

            act_ext = xml.SubElement(ext, _activity_ext_ns('LX'))

            if 'speed_avg' in lap:
                avg_speed = xml.SubElement(act_ext, _activity_ext_ns('AvgSpeed'))
                avg_speed.text = str(kph_to_ms(float(lap['speed_avg'])))


            if 'cad_max' in lap:

                if activity_type == 'ride':
                    max_cad = xml.SubElement(act_ext, _activity_ext_ns('MaxBikeCadence'))
                    max_cad.text = str(lap['cad_max'])
                elif activity_type == 'run':
                    max_cad = xml.SubElement(act_ext, _activity_ext_ns('MaxRunCadence'))
                    max_cad.text = str(lap['cad_max'])

                    avg_cad = xml.SubElement(act_ext, _activity_ext_ns('AvgRunCadence'))
                    avg_cad.text = str(lap['cad_avg'])


            if 'pwr_max' in lap:

                avg_pwr = xml.SubElement(act_ext, _activity_ext_ns('AvgWatts'))
                avg_pwr.text = str(lap['pwr_avg'])

                max_pwr = xml.SubElement(act_ext, _activity_ext_ns('MaxWatts'))
                max_pwr.text = str(lap['pwr_max'])



    if device is not None:

        # Except for the name i don't know what values to add here
        # so i just add some values from the BrytonBridge device info.

        creator = xml.SubElement(activity, _ns('Creator'))
        creator.set(_ns_xsi('type'), 'Device_t')

        xml.SubElement(creator, _ns('Name')).text = 'Bryton '+device['name']

        xml.SubElement(creator, _ns('UnitId')).text = device['serial']

        product_id = ''
        if 'Rider' in device['name']:
            product_id += '1'
        else:
            product_id += '2'

        num = re.search(r'\d+$', device['name'])
        product_id += num.group(0) if num is not None else '0'

        xml.SubElement(creator, _ns('ProductID')).text = product_id

        version = xml.SubElement(creator, _ns('Version'))


        v1 = re.search(r'\d+', device['rev'])
        xml.SubElement(version, _ns('VersionMajor')).text = v1.group(0) if v1 is not None else '1'
        v2 = re.search(r'\d+', device['firmware'])
        xml.SubElement(version, _ns('VersionMinor')).text = v2.group(0) if v2 is not None else '1'
        xml.SubElement(version, _ns('BuildMajor')).text = '0'
        xml.SubElement(version, _ns('BuildMinor')).text = '0'


    app = xml.SubElement(root, _ns('Author'))
    app.set(_ns_xsi('type'), 'Application_t')

    xml.SubElement(app, _ns('Name')).text = 'BrytonOffline'
    build = xml.SubElement(app, _ns('Build'))

    version = xml.SubElement(build, _ns('Version'))


    v1,v2 = VERSION.split('.')[0:2]

    xml.SubElement(version, _ns('VersionMajor')).text = v1
    xml.SubElement(version, _ns('VersionMinor')).text = v2
    xml.SubElement(version, _ns('BuildMajor')).text = '0'
    xml.SubElement(version, _ns('BuildMinor')).text = '0'

    xml.SubElement(build, _ns('Type')).text = 'Release'


    xml.SubElement(app, _ns('LangID')).text = 'EN'
    xml.SubElement(app, _ns('PartNumber')).text = '000-0000-00'


    if pretty:
        indent_element_tree(root)


    return "<?xml version='1.0' encoding='utf-8'?>\n"+xml.tostring(root)






