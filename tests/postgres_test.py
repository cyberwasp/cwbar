import os
import unittest

import cwbar.config
import cwbar.postgres

cwbar.config.PG_PASS = os.path.join(os.path.dirname(__file__), "data", "pgpass")


class SourceProjectTest(unittest.TestCase):

    def test_lookup_user_pass(self):
        u_p = cwbar.postgres.lookup_user_pass("localhost", "5432", "any")
        self.assertEqual(["sysdba", "pass1"], u_p)
