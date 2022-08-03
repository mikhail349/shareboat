from django.test import TestCase
from file.utils import limit_size, get_file_path

class TestCase(TestCase):
    
    def test_limit_size(self):
        # width limit
        self.assertEqual(limit_size(2000, 1000, 1000, 1000), (1000, 500))
        # height limit
        self.assertEqual(limit_size(1000, 2000, 1000, 1000), (500, 1000))
        # no limit
        self.assertEqual(limit_size(123, 456, 1000, 1000), (123, 456))

    def test_get_file_path(self):
        res = get_file_path(None, None, 'somepath/')
        self.assertTrue(res.startswith('somepath/') and res.endswith('.webp'))