
import unittest

import tcx_templates
import tcx
import xml_testing
from xml.etree import ElementTree

from utils import stripws_element_tree

class GPXMock(object):



    def __init__(self, laps):
        self.laps = laps


    def getSummary(self):
        return tcx_templates.SUMMARY



    def getTrackPoints(self):

        return self.laps



class TestTCX(unittest.TestCase):




    def test_simple_lap_no_speed(self):

        gpx = GPXMock(tcx_templates.SIMPLE_NO_SPEED_LAPS)

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_NO_SPEED_RESULT.format(sport='Biking'),
                tcx.bryton_gpx_to_tcx(gpx, pretty=True)))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_NO_SPEED_RESULT.format(sport='Running'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='run', pretty=True)))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_NO_SPEED_RESULT.format(sport='Other'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='other', pretty=True)))


    def test_simple_lap_with_speed(self):


        gpx = GPXMock(tcx_templates.SIMPLE_SPEED_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_SPEED_RESULT.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)
            ))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_SPEED_RESULT.format(sport='Running'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='run', pretty=True)
            ))
        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_SPEED_RESULT.format(sport='Other'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='other', pretty=True)
            ))


    def test_with_device(self):


        gpx = GPXMock(tcx_templates.SIMPLE_SPEED_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_SPEED_RESULT_WITH_DEVICE.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True, device={
                'name' : 'Rider40',
                'serial' : '12345',
                'rev' : '005',
                'firmware' : 'R026',
            })
            ))



    def test_simple_lap_with_hr(self):


        gpx = GPXMock(tcx_templates.SIMPLE_HR_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_HR_RESULT.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)
            ))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_HR_RESULT.format(sport='Running'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='run', pretty=True)
            ))
        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_HR_RESULT.format(sport='Other'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='other', pretty=True)
            ))




    def test_simple_lap_with_pwr(self):


        gpx = GPXMock(tcx_templates.SIMPLE_PWR_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_PWR_RESULT.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)
            ))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_PWR_RESULT.format(sport='Running'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='run', pretty=True)
            ))
        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_PWR_RESULT.format(sport='Other'),
            tcx.bryton_gpx_to_tcx(gpx, activity_type='other', pretty=True)
            ))







    def test_lap_with_cadence(self):


        gpx = GPXMock(tcx_templates.SIMPLE_CADENCE_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_CADENCE_RESULT_BIKING,
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)
            ))

        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_CADENCE_RESULT_RUNNING,
            tcx.bryton_gpx_to_tcx(gpx, activity_type='run', pretty=True)
            ))




    def test_lap_with_pause(self):


        gpx = GPXMock(tcx_templates.SIMPLE_WITH_PAUSE)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_WITH_PAUSE_RESULT.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)))


    def test_lap_with_multiple_laps(self):


        gpx = GPXMock(tcx_templates.SIMPLE_WITH_MULTIPLE_LAPS)


        self.assertTrue(xml_testing.compare_xml_strings(
            tcx_templates.SIMPLE_WITH_MULTIPLE_LAPS_RESULT.format(sport='Biking'),
            tcx.bryton_gpx_to_tcx(gpx, pretty=True)))


