import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
CDN_DIR = os.path.join(ROOT, 'cdn')
if CDN_DIR not in sys.path:
    sys.path.insert(0, CDN_DIR)

from cdn.utils.packet_functions import (
    PacketSizes,
    form_packet,
    seq_num_from_packet,
    ack_num_from_packet,
    payload_from_packet,
    ack_flag_from_packet,
    syn_flag_from_packet,
    fin_flag_from_packet,
)


class TestPacketFunctions(unittest.TestCase):
    def test_form_and_parse_packet(self):
        payload = b'hello-cdn'
        packet = form_packet(10, 20, payload, ack=True, syn=True, fin=False)

        self.assertEqual(seq_num_from_packet(packet), 10)
        self.assertEqual(ack_num_from_packet(packet), 20)
        self.assertEqual(payload_from_packet(packet), payload)
        self.assertTrue(ack_flag_from_packet(packet))
        self.assertTrue(syn_flag_from_packet(packet))
        self.assertFalse(fin_flag_from_packet(packet))

    def test_header_size_constant(self):
        payload = b''
        packet = form_packet(1, 1, payload)
        self.assertEqual(len(packet), PacketSizes.HEADER.value)


if __name__ == '__main__':
    unittest.main()
