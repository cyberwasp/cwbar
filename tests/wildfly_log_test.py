import os
import unittest

import cwbar.wildfly_log


class TestLog(unittest.TestCase):

    def test_log_creation(self):
        with open(os.path.join("data", "server.log")) as f:
            data = f.read()
        log = cwbar.wildfly_log.LogFile(data)
        e0 = log.entries[0]
        self.assertEqual(len(log.entries), 9)
        self.assertEqual(e0.source, "org.jboss.as.ejb3.deployment.processors.EjbJndiBindingsDeploymentUnitProcessor")
