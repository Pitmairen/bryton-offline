
import copy


import version

SUMMARY = {
    'start' : '2012-01-01T01:01:01Z',
    'end' : '2012-01-01T02:01:01Z',
    'total_time' : 60*60,
    'distance' : 25000.0,
    'speed_max' : 25.2,
    'speed_avg' : 20.1,
    'calories' : 400,
}



_LAP = SUMMARY.copy()
del _LAP['speed_max']
del _LAP['speed_avg']
_LAP['track_points'] = [
    {'time' : '2012-01-01T01:01:01Z', 'lat' : 60.123, 'lon' : 1.123, 'ele' : 63},
    {'time' : '2012-01-01T01:01:02Z', 'lat' : 60.124, 'lon' : 1.124, 'ele' : 63},
]


SIMPLE_NO_SPEED_LAPS = [_LAP]
SIMPLE_NO_SPEED_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])






_POINTS = copy.deepcopy(_LAP['track_points'])
_LAP = SUMMARY.copy()

for p, speed in zip(_POINTS, [22.0]*len(_POINTS)):
    p['spd'] = speed
_LAP['track_points'] = _POINTS


SIMPLE_SPEED_LAPS = [_LAP]
SIMPLE_SPEED_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
          </a:LX>
        </Extensions>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])








_POINTS = copy.deepcopy(_LAP['track_points'])
_LAP = SUMMARY.copy()
_LAP['hr_avg'] = 130
_LAP['hr_max'] = 150
for p, hr in zip(_POINTS, [140]*len(_POINTS)):
    p['hrm'] = hr
_LAP['track_points'] = _POINTS


SIMPLE_HR_LAPS = [_LAP]
SIMPLE_HR_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <AverageHeartRateBpm>
          <Value>130</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>150</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
          </a:LX>
        </Extensions>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])









_POINTS = copy.deepcopy(_LAP['track_points'])
_LAP = _LAP.copy()
_LAP['pwr_avg'] = 150
_LAP['pwr_max'] = 250
for p, pwr in zip(_POINTS, [140]*len(_POINTS)):
    p['pwr'] = pwr
_LAP['track_points'] = _POINTS


SIMPLE_PWR_LAPS = [_LAP]
SIMPLE_PWR_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <AverageHeartRateBpm>
          <Value>130</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>150</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
            <a:AvgWatts>150</a:AvgWatts>
            <a:MaxWatts>250</a:MaxWatts>
          </a:LX>
        </Extensions>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])












_POINTS = copy.deepcopy(_LAP['track_points'])
_LAP = _LAP.copy()
_LAP['cad_avg'] = 78
_LAP['cad_max'] = 78
for p, speed in zip(_POINTS, [78]*len(_POINTS)):
    p['cad'] = speed
_LAP['track_points'] = _POINTS


SIMPLE_CADENCE_LAPS = [_LAP]
SIMPLE_CADENCE_RESULT_BIKING = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="Biking">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <AverageHeartRateBpm>
          <Value>130</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>150</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <Cadence>78</Cadence>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Cadence>78</Cadence>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Cadence>78</Cadence>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
            <a:MaxBikeCadence>78</a:MaxBikeCadence>
            <a:AvgWatts>150</a:AvgWatts>
            <a:MaxWatts>250</a:MaxWatts>
          </a:LX>
        </Extensions>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])
SIMPLE_CADENCE_RESULT_RUNNING = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="Running">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <AverageHeartRateBpm>
          <Value>130</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>150</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:RunCadence>78</a:RunCadence>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <HeartRateBpm>
              <Value>140</Value>
            </HeartRateBpm>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
                <a:RunCadence>78</a:RunCadence>
                <a:Watts>140</a:Watts>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
            <a:MaxRunCadence>78</a:MaxRunCadence>
            <a:AvgRunCadence>78</a:AvgRunCadence>
            <a:AvgWatts>150</a:AvgWatts>
            <a:MaxWatts>250</a:MaxWatts>
          </a:LX>
        </Extensions>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])


SIMPLE_SPEED_RESULT_WITH_DEVICE = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:a="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="Biking">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <MaximumSpeed>7.0</MaximumSpeed>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
            <Extensions>
              <a:TPX>
                <a:Speed>6.11111111111</a:Speed>
              </a:TPX>
            </Extensions>
          </Trackpoint>
        </Track>
        <Extensions>
          <a:LX>
            <a:AvgSpeed>5.58333333333</a:AvgSpeed>
          </a:LX>
        </Extensions>
      </Lap>
      <Creator xsi:type="Device_t">
        <Name>Bryton Rider40</Name>
        <UnitId>12345</UnitId>
        <ProductID>140</ProductID>
        <Version>
          <VersionMajor>005</VersionMajor>
          <VersionMinor>026</VersionMinor>
          <BuildMajor>0</BuildMajor>
          <BuildMinor>0</BuildMinor>
        </Version>
      </Creator>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])





_LAP = SUMMARY.copy()
del _LAP['speed_max']
del _LAP['speed_avg']
_LAP['track_points'] = [
    {'time' : '2012-01-01T01:01:01Z', 'lat' : 60.123, 'lon' : 1.123, 'ele' : 63},
    {'time' : '2012-01-01T01:01:02Z', 'lat' : 60.124, 'lon' : 1.124, 'ele' : 63},
    None,
    {'time' : '2012-01-01T01:01:03Z', 'lat' : 60.123, 'lon' : 1.123, 'ele' : 63},
    {'time' : '2012-01-01T01:01:04Z', 'lat' : 60.124, 'lon' : 1.124, 'ele' : 63},
]


SIMPLE_WITH_PAUSE = [_LAP]
SIMPLE_WITH_PAUSE_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
        </Track>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:03Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:04Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])









_LAPS = []


for i in range(2):

    _LAP = SUMMARY.copy()
    del _LAP['speed_max']
    del _LAP['speed_avg']
    _LAP['track_points'] = [
        {'time' : '2012-01-01T01:01:01Z', 'lat' : 60.123, 'lon' : 1.123, 'ele' : 63},
        {'time' : '2012-01-01T01:01:02Z', 'lat' : 60.124, 'lon' : 1.124, 'ele' : 63},
    ]
    _LAPS.append(_LAP)

SIMPLE_WITH_MULTIPLE_LAPS = _LAPS
SIMPLE_WITH_MULTIPLE_LAPS_RESULT = """\
<?xml version='1.0' encoding='utf-8'?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd">
  <Activities>
    <Activity Sport="{{sport}}">
      <Id>2012-01-01T01:01:01Z</Id>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
        </Track>
      </Lap>
      <Lap StartTime="2012-01-01T01:01:01Z">
        <TotalTimeSeconds>3600.0</TotalTimeSeconds>
        <DistanceMeters>25000.0</DistanceMeters>
        <Calories>400</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2012-01-01T01:01:01Z</Time>
            <Position>
              <LatitudeDegrees>60.123</LatitudeDegrees>
              <LongitudeDegrees>1.123</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
          <Trackpoint>
            <Time>2012-01-01T01:01:02Z</Time>
            <Position>
              <LatitudeDegrees>60.124</LatitudeDegrees>
              <LongitudeDegrees>1.124</LongitudeDegrees>
            </Position>
            <AltitudeMeters>63.0</AltitudeMeters>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>BrytonOffline</Name>
    <Build>
      <Version>
        <VersionMajor>{0}</VersionMajor>
        <VersionMinor>{1}</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>
""".format(*version.VERSION.split('.')[0:2])



