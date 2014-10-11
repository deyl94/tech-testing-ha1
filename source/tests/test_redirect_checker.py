import unittest
import mock
import os
from mock import patch
import redirect_checker


class RedirectCheckerTestCase(unittest.TestCase):
    
    @patch.object(os, 'path', mock.MagicMock())
    @patch('redirect_checker.parse_cmd_args')
    @patch('redirect_checker.daemonize')
    @patch('redirect_checker.create_pidfile')
    @patch('redirect_checker.load_config_from_pyfile')
    @patch('redirect_checker.dictConfig')
    @patch('redirect_checker.main_loop')
    def test_main(self, main_loop, dictConfig,
    				load_config_from_pyfile, create_pidfile,
    				daemonize, parse_cmd_args):
    	argv = [1, 2, 3] 

    	args = mock.MagicMock()
    	args.daemon = True
    	args.pidfile = 42	

    	logging = mock.Mock()

    	config = mock.MagicMock()
    	config.LOGGING = logging
    	config.EXIT_CODE = 42

    	parse_cmd_args.return_value = args
    	load_config_from_pyfile.return_value = config

    	assert 42 == redirect_checker.main(argv)
    	parse_cmd_args.assert_called_once_with(argv[1:])
    	daemonize.assert_called_once_with()
    	create_pidfile.assert_called_once_with(args.pidfile)
    	dictConfig.assert_called_once_with(logging)
    	main_loop.assert_called_once_with(config)

    @patch('redirect_checker.worker', mock.Mock())
    @patch('redirect_checker.logger', mock.MagicMock())
    @patch.object(os, 'getpid')
    @patch('redirect_checker.check_network_status')
    @patch('redirect_checker.active_children')
    @patch('redirect_checker.spawn_workers')
    @patch('redirect_checker.sleep')
    def test_main_loop(self, sleep, spawn_workers, active_children,
                        check_network_status, getpid):
        child = mock.MagicMock()
        active_children = [child, child, child]

        def test_case_complete(*args, **kwargs):
            redirect_checker.test_case_complete = True
        sleep.side_effect = test_case_complete

        check_network_status.return_value = True


        config = mock.MagicMock()
        config.WORKER_POOL_SIZE = 4
        config.CHECK_URL = 1
        config.HTTP_TIMEOUT = 1
        config.SLEEP = 1

        getpid.return_value = 42

        redirect_checker.main_loop(config)
        assert spawn_workers.call_count == 1
        redirect_checker.test_case_complete = False

    @patch('redirect_checker.worker', mock.Mock())
    @patch('redirect_checker.logger', mock.MagicMock())
    @patch.object(os, 'getpid')
    @patch('redirect_checker.check_network_status')
    @patch('redirect_checker.active_children')
    @patch('redirect_checker.spawn_workers')
    @patch('redirect_checker.sleep')
    def test_main_loop_else(self, sleep, spawn_workers, active_children,
                        check_network_status, getpid):
        child = mock.MagicMock()
        active_children.return_value = [child, child, child]

        def test_case_complete(*args, **kwargs):
            redirect_checker.test_case_complete = True
        sleep.side_effect = test_case_complete

        check_network_status.return_value = False

        config = mock.MagicMock()
        config.WORKER_POOL_SIZE = 4
        config.CHECK_URL = 1
        config.HTTP_TIMEOUT = 1
        config.SLEEP = 1

        getpid.return_value = 42

        redirect_checker.main_loop(config)
        assert 3 == child.terminate.call_count
        redirect_checker.test_case_complete = False