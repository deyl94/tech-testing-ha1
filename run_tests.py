#!/usr/bin/env python2.7

import os
import sys
import unittest

source_dir = os.path.join(os.path.dirname(__file__), 'source')
sys.path.insert(0, source_dir)

from source.tests.test_notification_pusher import NotificationPusherTestCase
from source.tests.test_redirect_checker import RedirectCheckerTestCase
from source.tests.test_utils import *


if __name__ == '__main__':
    suite = unittest.TestSuite((
        unittest.makeSuite(NotificationPusherTestCase),
        unittest.makeSuite(RedirectCheckerTestCase),

        unittest.makeSuite(DaemonizeTestCase),
        unittest.makeSuite(CreatePidfileTestCase),
        unittest.makeSuite(LoadConfigFromPyfileTestCase),
        unittest.makeSuite(ParseCmdArgsTestCase),
        unittest.makeSuite(GetTubeTestCase),
        unittest.makeSuite(SpawnWorkersTestCase),
        unittest.makeSuite(CheckNetworkStatusTestCase),

    ))
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
