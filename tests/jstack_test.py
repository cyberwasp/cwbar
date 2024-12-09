import os
import unittest

import cwbar.java.jstack


class TestLog(unittest.TestCase):

    def test_log_creation(self):
        jstack = cwbar.java.jstack.JStack(os.path.join(os.path.dirname(__file__), "data", "jstack.log"))
        stack_traces = jstack.stack_traces
        self.assertEqual(len(stack_traces), 9)