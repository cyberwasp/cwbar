import os
import unittest

import cwbar.settings
import cwbar.postgres

cwbar.settings.PG_PASS = os.path.abspath(os.path.join("data", "pgpass"))


class SourceProjectTest(unittest.TestCase):

    def test_lookup_user_pass(self):
        u_p = cwbar.postgres.lookup_user_pass("localhost", "5432", "any")
        self.assertEqual(["sysdba", "pass1"], u_p)
