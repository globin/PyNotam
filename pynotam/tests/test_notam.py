import datetime
import unittest
from .. import Notam
from .test_helper import read_single_notam


class TestNotam(unittest.TestCase):
    def test_parsed_fields(self) -> None:
        expected_values = {
            'A0623/91' : {
                'notam_id' : 'A0623/91',
                'notam_type' : 'NEW',
                'fir' : 'EGXX',
                'notam_code' : 'QRDCA',
                'traffic_type' : set(['IFR', 'VFR']),
                'purpose' : set(['IMMEDIATE ATTENTION', 'OPERATIONAL SIGNIFICANCE', 'FLIGHT OPERATIONS']),
                'scope' : set(['NAV WARNING']),
                'fl_lower' : 0,
                'fl_upper' : 400,
                'area' : {'lat' : '5510N', 'long' : '00520W', 'radius' : 50},
                'location' : ['EGTT', 'EGPX'],
                'valid_from' : datetime.datetime(1991, 4, 3, 7, 30, tzinfo=datetime.timezone.utc),
                'valid_till' : datetime.datetime(1991, 4, 28, 15, 0, tzinfo=datetime.timezone.utc),
                'schedule' : 'APR 03 07 12 21 24 AND 28 0730 TO 1500',
                'body' : 'DANGER AREA DXX IS ACTIVE',
                'limit_lower' : 'GND',
                'limit_upper' : '12 200 m (40 000 ft) MSL.',
                'created': None,
                'source': None,
            },
            '476008' : {
                'notam_id' : 'A0126/15',
                'notam_type' : 'REPLACE',
                'ref_notam_id' : 'A0074/14',
                'fir' : 'LLLL',
                'notam_code' : 'QARAU',
                'traffic_type' : set(['IFR', 'VFR']),
                'purpose' : set(['IMMEDIATE ATTENTION', 'OPERATIONAL SIGNIFICANCE', 'FLIGHT OPERATIONS']),
                'scope' : set(['EN-ROUTE']),
                'fl_lower' : 0,
                'fl_upper' : 999,
                'area' : {'lat' : '3250N', 'long' : '03459E', 'radius' : 1},
                'location' : ['LLLL'],
                'valid_from' : datetime.datetime(2015, 1, 13, 9, 1, tzinfo=datetime.timezone.utc),
                'valid_till' : datetime.datetime.max,
                'schedule' : None,
                'body' : 'ATS RTE `H4A` NOT AVBL UFN.',
                'limit_lower' : None,
                'limit_upper' : None,
                'created': None,
                'source': None,
            },
            'C2661/23' : {
                'notam_id' : 'C2661/23',
                'notam_type' : 'NEW',
                'fir' : 'EDMM',
                'notam_code' : 'QOBCE',
                'traffic_type' : set(['IFR', 'VFR']),
                'purpose' : set(['MISC']),
                'scope' : set(['AERODROME', 'EN-ROUTE']),
                'fl_lower' : 0,
                'fl_upper' : 11,
                'area' : {'lat' : '4955N', 'long' : '01055E', 'radius' : 5},
                'location' : ['EDQA'],
                'valid_from' : datetime.datetime(2023, 8, 9, 4, 0, tzinfo=datetime.timezone.utc),
                'valid_till' : datetime.datetime(2023, 11, 9, 23, 59, tzinfo=datetime.timezone.utc),
                'schedule' : None,
                'body' : 'HIGH CRANES ERECTED WI GLIDER TFC PATTERN. PSN 495451N 0105449E\nAND 495451N 0105450E. 0.3NM S OF ARP. ELEV 1001FT/197FT AGL. DAY AND\nNIGHT MARKED.',
                'limit_lower' : None,
                'limit_upper' : None,
                'created': datetime.datetime(2023, 8, 8, 13, 5, tzinfo=datetime.timezone.utc),
                'source': 'EUECYIYN',
            }
        }

        for (notam_to_test, expected) in expected_values.items():
            notam_text = read_single_notam(notam_to_test)
            n = Notam.from_str(notam_text)
            for (field, value) in expected.items():
                with self.subTest(msg='Field "{}" of NOTAM "{}"'.format(field, notam_to_test)):
                    self.assertEqual(getattr(n, field), value, msg='Field "{}" of NOTAM "{}"'.format(field, notam_to_test))
