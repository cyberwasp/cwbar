import os
import unittest

from cwbar.wildfly_config import WildflyConfig


class WildflyConfigTest(unittest.TestCase):

    def test_get_data_sources(self):
        c = WildflyConfig("tests", os.path.join("data", "standalone-full.xml"))
        data_sources = list(c.get_data_sources())
        self.assertEqual(len(data_sources), 3)
        self.assertEqual(data_sources[1].get_driver(), "postgresql-42.0.0.jar")
        self.assertEqual(data_sources[1].get_connection(), "jdbc:postgresql://172.17.14.19:5432/rebudget_mo3")
        self.assertEqual(data_sources[1].get_user(), "sysdba")
        self.assertEqual(data_sources[1].get_password(), "masterkey")
        self.assertEqual(data_sources[1].get_host(), "172.17.14.19")
        self.assertEqual(data_sources[1].get_port(), "5432")
        self.assertEqual(data_sources[1].get_db(), "rebudget_mo3")


if __name__ == '__main__':
    unittest.main()
