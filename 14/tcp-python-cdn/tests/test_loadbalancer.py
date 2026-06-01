import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
CDN_DIR = os.path.join(ROOT, 'cdn')
if CDN_DIR not in sys.path:
    sys.path.insert(0, CDN_DIR)

import cdn.loadbalancer as lb


class TestLoadBalancer(unittest.TestCase):
    def setUp(self):
        lb.server_map.clear()

    def test_find_best_server_endpoint(self):
        lb.server_map['10.0.0.1:33001'] = 10.0
        lb.server_map['10.0.0.2:33002'] = 5.0
        lb.server_map['10.0.0.3:33003'] = 20.0
        self.assertEqual(lb.find_best_server_endpoint(), '10.0.0.2:33002')

    def test_find_best_server_endpoint_none_when_all_zero(self):
        lb.server_map['10.0.0.1:33001'] = 0.0
        lb.server_map['10.0.0.2:33002'] = 0.0
        self.assertEqual(lb.find_best_server_endpoint(), '')

    @patch('cdn.loadbalancer.probe_server_preference')
    def test_update_server_map(self, mock_probe):
        lb.server_map['10.0.0.1:33001'] = 0.0
        lb.server_map['10.0.0.2:33002'] = 0.0
        mock_probe.side_effect = [12.5, 33.3]

        lb.update_server_map()

        self.assertEqual(lb.server_map['10.0.0.1:33001'], 12.5)
        self.assertEqual(lb.server_map['10.0.0.2:33002'], 33.3)


if __name__ == '__main__':
    unittest.main()
