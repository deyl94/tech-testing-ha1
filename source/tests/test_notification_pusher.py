import unittest
import mock
import json
import tarantool
import os
import tarantool_queue
from mock import Mock
from mock import patch
import notification_pusher
import requests

import gevent
from notification_pusher import create_pidfile
from notification_pusher import load_config_from_pyfile

class NotificationPusherTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch('notification_pusher.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)):
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    @patch('source.lib.utils.argparse.ArgumentParser.parse_args')
    def test_parse_cmd_args(self, parser):
        args = 'args'
        notification_pusher.parse_cmd_args(args)
        parser.assert_called_once_with(args=args)

    @patch('__builtin__.execfile')
    @patch('notification_pusher.Config')
    def test_load_config_from_pyfile(self, Config, execfile):
        path = '/t/e/s/t'
        cfg = Config()
        result = load_config_from_pyfile(path)
        
        execfile.assert_called_once_with(path, {})
        assert result == cfg

    @patch.object(gevent, 'signal')
    def test_install_signal_handlers(self, signal):
        notification_pusher.install_signal_handlers()
        assert signal.call_count == 4

    def test_stop_handler(self):
        offset = notification_pusher.SIGNAL_EXIT_CODE_OFFSET
        signal = 42
        run_application = notification_pusher.run_application,
        exit_code = notification_pusher.exit_code
        notification_pusher.stop_handler(signal)
        assert notification_pusher.run_application == False
        assert notification_pusher.exit_code == (offset + signal)
        notification_pusher.run_application = run_application
        notification_pusher.exit_code = exit_code

    def test_done_with_processed_tasks(self):
        task_mock = Mock()
        task_mock.action_name = Mock()
        action_name = 'action_name'
        
        task_queue_mock = mock.MagicMock()
        task_queue_mock.qsize.return_value = 1
        task_queue_mock.get_nowait.return_value = (task_mock, action_name)
        
        notification_pusher.done_with_processed_tasks(task_queue_mock);
        task_mock.action_name.assert_called_once_with()

    @patch('notification_pusher.logger')
    def test_done_with_processed_tasks_error_data_base(self, logger):
        task_mock = Mock()
        err = tarantool.DatabaseError()
        task_mock.action_name = Mock(side_effect = err)
        action_name = 'action_name'
        
        task_queue_mock = mock.MagicMock()
        task_queue_mock.qsize.return_value = 1
        task_queue_mock.get_nowait.return_value = (task_mock, action_name)
        
        notification_pusher.done_with_processed_tasks(task_queue_mock)
        logger.exception.assert_called_once_with(err)

    @patch('notification_pusher.logger')
    def test_done_with_processed_tasks_error_empty_queue(self, logger):
        task_queue_mock = mock.MagicMock()
        task_queue_mock.qsize.return_value = 1
        task_queue_mock.get_nowait.side_effect = gevent.queue.Empty
        
        notification_pusher.done_with_processed_tasks(task_queue_mock);
        assert logger.debug.call_count == 1

    @patch.object(requests, 'post')
    @patch('threading.current_thread')
    def test_notification_worker(self, current_thread, post):
        id = 42
        url = 'url'
        data = {'callback_url': url}
        result_data = json.dumps({"id": id})
        
        task_queue_mock = Mock()

        task_mock = mock.MagicMock()
        task_mock.data.copy.return_value = data
        task_mock.task_id = id

        notification_pusher.notification_worker(task_mock, task_queue_mock)
        post.assert_called_once_with(url, data=result_data)
        task_queue_mock.put.assert_called_once_with((task_mock, 'ack'))

    @patch.object(requests, 'post')
    @patch('threading.current_thread')
    @patch('notification_pusher.logger')
    def test_notification_worker_error_request(self, logger, current_thread, post):
        err = requests.RequestException()
        task_queue_mock = Mock()

        task_mock = mock.MagicMock()
        task_mock.data.copy.side_effect = err

        notification_pusher.notification_worker(task_mock, task_queue_mock)
        logger.exception.assert_called_once_with(err)
        task_queue_mock.put.assert_called_once_with((task_mock, 'bury'))

    @patch.object(os, '_exit')
    @patch.object(os, 'setsid')
    @patch.object(os, 'fork')
    def test_daemonize(self, os_fork, os_setsid, os_exit):
        os_fork.side_effect = [0, 1]

        notification_pusher.daemonize()
        os_setsid.assert_called_once_with()
        os_exit.assert_called_once_with(0)
    
    @patch.object(os, '_exit')
    @patch.object(os, 'fork')
    def test_daemonize_else(self, os_fork, os_exit):
        os_fork.return_value = 42

        notification_pusher.daemonize()
        os_exit.assert_called_once_with(0)

    @patch.object(os, 'fork')   
    def test_daemonize_error_os(self, os_fork):
        os_fork.side_effect = OSError
        self.assertRaises(Exception, notification_pusher.daemonize)

    @patch.object(os, 'setsid')
    @patch.object(os, 'fork')   
    def test_daemonize_if_error_os(self, os_fork, os_setsid):
        os_fork.side_effect = [0, OSError]
        self.assertRaises(Exception, notification_pusher.daemonize)
        os_setsid.assert_called_once_with()


    @patch('notification_pusher.logger')
    @patch('notification_pusher.notification_worker', Mock())
    @patch('notification_pusher.sleep')
    @patch('notification_pusher.Greenlet')
    @patch('notification_pusher.Pool')
    @patch.object(gevent.queue, 'Queue')
    @patch.object(tarantool_queue, 'Queue')
    @patch('notification_pusher.done_with_processed_tasks')
    def test_main_loop(self, done_with_processed_tasks, tarantool_queue, 
                    gevent_queue, gevent_pool, gevent_greenlet, gevent_sleep, logger):
        config_mock = mock.MagicMock()
        config_mock.QUEUE_HOST = 1
        config_mock.QUEUE_PORT = 1
        config_mock.QUEUE_SPACE = 1
        config_mock.QUEUE_TUBE = 1
        config_mock.SLEEP = 1
        config_mock.WORKER_POOL_SIZE = 1

        #STOP WHILE
        def change_state(*args, **kwargs):
            notification_pusher.run_application = False
        gevent_sleep.side_effect = change_state

        worker_mock = mock.MagicMock()
        gevent_greenlet.return_value = worker_mock

        worker_pool_mock = mock.MagicMock()
        worker_pool_mock.free_count.return_value = 1
        
        task_mock = mock.MagicMock()
        task_mock.task_id = 42
        task_mock.number = 42

        tube_mock = mock.MagicMock()
        tube_mock.take.return_value = task_mock

        queue = Mock()
        queue.return_value = tube_mock

        tarantool_queue.return_value = queue

        gevent_pool.return_value = worker_pool_mock

        processed_task_mock = Mock()
        gevent_queue.return_value = processed_task_mock

        notification_pusher.main_loop(config_mock)
        worker_pool_mock.add.assert_called_once_with(worker_mock)
        worker_mock.start.assert_called_once_with()
        done_with_processed_tasks.assert_called_once_with(processed_task_mock)

        notification_pusher.run_application = True


    @patch('notification_pusher.daemonize')
    @patch('notification_pusher.create_pidfile')
    @patch('notification_pusher.load_config_from_pyfile')
    @patch('notification_pusher.patch_all')
    @patch('notification_pusher.dictConfig')
    @patch('notification_pusher.parse_cmd_args')
    @patch('notification_pusher.current_thread')
    @patch('notification_pusher.install_signal_handlers')
    @patch('notification_pusher.main_loop')
    @patch('notification_pusher.sleep')
    @patch('notification_pusher.logger')
    @patch.object(os, 'path', mock.MagicMock())
    def test_main(self, logger, sleep, main_loop, install_signal_handlers,
                    current_thread, parse_cmd_args, dictConfig,
                    patch_all, load_config_from_pyfile, create_pidfile,
                    daemonize):

        def change_state(*args, **kwargs):
            notification_pusher.run_application = False

        main_loop.side_effect = change_state

        argv = [1, 2, 3, 4]
        exit_code = notification_pusher.exit_code
        notification_pusher.exit_code = 42

        config = Mock()
        config.LOGGING = Mock()
        load_config_from_pyfile.return_value = config

        cmds = mock.MagicMock()
        cmds.daemon = True
        cmds.pidfile = 2
        parse_cmd_args.return_value = cmds

        assert 42 == notification_pusher.main(argv)
        daemonize.assert_called_once_with()
        parse_cmd_args.assert_called_once_with(argv[1:])
        create_pidfile.assert_called_once_with(cmds.pidfile)
        patch_all.assert_called_once_with()
        install_signal_handlers.assert_called_once_with()
        main_loop.assert_called_once_with(config)
        
        notification_pusher.exit_code = exit_code
        notification_pusher.run_application = True

    @patch.object(os, 'path', mock.MagicMock())
    @patch('notification_pusher.daemonize')
    @patch('notification_pusher.create_pidfile')
    @patch('notification_pusher.load_config_from_pyfile')
    @patch('notification_pusher.patch_all')
    @patch('notification_pusher.dictConfig')
    @patch('notification_pusher.parse_cmd_args')
    @patch('notification_pusher.current_thread')
    @patch('notification_pusher.install_signal_handlers')
    @patch('notification_pusher.main_loop')
    @patch('notification_pusher.sleep')
    @patch('notification_pusher.logger')
    def test_main_error(self, logger, sleep, main_loop, install_signal_handlers,
                    current_thread, parse_cmd_args, dictConfig,
                    patch_all, load_config_from_pyfile, create_pidfile,
                    daemonize):

        def change_state(*args, **kwargs):
            notification_pusher.run_application = False

        main_loop.side_effect = Exception
        sleep.side_effect = change_state

        argv = [1, 2, 3, 4]
        exit_code = notification_pusher.exit_code
        notification_pusher.exit_code = 42

        config = Mock()
        config.LOGGING = Mock()
        config.SLEEP_ON_FAIL = 1
        load_config_from_pyfile.return_value = config

        cmds = mock.MagicMock()
        cmds.daemon = True
        cmds.pidfile = 2
        parse_cmd_args.return_value = cmds

        notification_pusher.main(argv)
        daemonize.assert_called_once_with()
        parse_cmd_args.assert_called_once_with(argv[1:])
        create_pidfile.assert_called_once_with(cmds.pidfile)
        patch_all.assert_called_once_with()
        install_signal_handlers.assert_called_once_with()
        sleep.assert_called_once_with(config.SLEEP_ON_FAIL)
        
        notification_pusher.exit_code = exit_code
        notification_pusher.run_application = True
