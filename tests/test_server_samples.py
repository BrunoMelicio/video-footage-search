import unittest
from unittest.mock import patch
from urllib.parse import urlparse

from server import selected_sample


class SampleSelectionTests(unittest.TestCase):
    def setUp(self):
        self.items = [{'id':'original','file':'samples/sample-reel.mp4'},
                      {'id':'lobby','file':'runtime/demo/lobby.mp4'}]

    def test_existing_sample_endpoint_keeps_original_default(self):
        with patch('server.review_samples', return_value=self.items):
            self.assertEqual(selected_sample(urlparse('/api/sample'))['id'], 'original')

    def test_selection_uses_only_catalog_entries(self):
        with patch('server.review_samples', return_value=self.items):
            self.assertEqual(selected_sample(urlparse('/api/sample?id=lobby'))['file'], 'runtime/demo/lobby.mp4')
            for value in ('missing', '../server.py', '%2Fetc%2Fpasswd'):
                self.assertIsNone(selected_sample(urlparse('/sample-preview.mp4?id='+value)))

    def test_unprepared_sample_is_unavailable(self):
        with patch('server.review_samples', return_value=self.items[:1]):
            self.assertIsNone(selected_sample(urlparse('/api/sample?id=lobby')))
