import os
import unittest

from cwbar import settings
from cwbar import postgres

settings.PG_PASS = os.path.abspath(os.path.join("data", "pgpass"))


class SourceProjectTest(unittest.TestCase):

    def test_lookup_user_pass(self):
        u_p = postgres.lookup_user_pass("localhost", "5432", "any")
        self.assertEqual(["sysdba", "pass1"], u_p)