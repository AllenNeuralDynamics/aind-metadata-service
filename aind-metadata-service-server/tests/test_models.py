"""Tests methods in models module"""

import unittest

from aind_metadata_service_server.models import HealthCheck


class TestHealthCheck(unittest.TestCase):
    """Tests for HealthCheck class"""

    def test_constructor(self):
        """Basic test for class constructor"""

        health_check = HealthCheck()
        self.assertEqual("OK", health_check.status)


if __name__ == "__main__":
    unittest.main()
