import unittest

import cwbar.arguments


class ArgumentsTest(unittest.TestCase):
    class __Server:
        def test1(self, only=False, non_clean=False): pass
        def test2(self, *args): pass
        def test3_1(self): pass

    __server = __Server()

    def test_create(self):
        arguments = cwbar.arguments.Arguments(["test", "--ssh=xz", "test1", "--only"])
        self.assertEqual("test", arguments.server_type())
        self.assertEqual({"ssh": "xz"}, arguments.server_kwargs())
        self.assertEqual("test1", arguments.command())
        self.assertEqual([], arguments.command_args(ArgumentsTest.__server.test1))
        self.assertEqual({"only": True}, arguments.command_kwargs(ArgumentsTest.__server.test1))

    def test_args(self):
        arguments = cwbar.arguments.Arguments(["test", "test2", "-c", "--dd=1"])
        self.assertEqual("test", arguments.server_type())
        self.assertEqual({}, arguments.server_kwargs())
        self.assertEqual("test2", arguments.command())
        self.assertEqual(["-c", "--dd=1"], arguments.command_args(ArgumentsTest.__server.test2))
        self.assertEqual({}, arguments.command_kwargs(ArgumentsTest.__server.test2))

    def test_name_with_dash(self):
        arguments = cwbar.arguments.Arguments(["test", "test3-1"])
        self.assertEqual("test", arguments.server_type())
        self.assertEqual("test3_1", arguments.command())
        self.assertEqual([], arguments.command_args(ArgumentsTest.__server.test3_1))
        self.assertEqual({}, arguments.command_kwargs(ArgumentsTest.__server.test3_1))


if __name__ == '__main__':
    unittest.main()
