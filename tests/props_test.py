import unittest

import cwbar.props

PARSE_DATA1 = """\
prop1=value1
prop2=value2.1 \\
       value2.2
"""


class SourceProjectTest(unittest.TestCase):
    def test_props_parse(self):
        props = cwbar.props.parse(PARSE_DATA1)
        self.assertEqual(props["prop2"], "value2.1 value2.2")
