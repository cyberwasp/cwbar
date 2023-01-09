import os
import unittest

import cwbar.wildfly.log


class TestLog(unittest.TestCase):

    def test_log_creation(self):
        log = cwbar.wildfly.log.LogFile(os.path.join(os.path.dirname(__file__), "data", "server.log"))
        e0 = log.entries[0]
        self.assertEqual(len(log.entries), 9)
        self.assertEqual(e0.source, "org.jboss.as.ejb3.deployment.processors.EjbJndiBindingsDeploymentUnitProcessor")

    def test_log_filter(self):
        log = cwbar.wildfly.log.LogFile(os.path.join(os.path.dirname(__file__), "data", "server.log"))
        res = list(log.filter("'Event' in e.source"))
        self.assertEqual(len(res), 2)
