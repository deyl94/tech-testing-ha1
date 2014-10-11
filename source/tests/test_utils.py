import unittest
import source.lib.utils
import mock
import socket
import urllib2

# daemonize() tests


class DaemonizeTestCase(unittest.TestCase):
    @mock.patch('source.lib.utils.os.fork', mock.Mock(side_effect=OSError()))
    def test_daemonize_fork_exception(self):
        with self.assertRaises(Exception):
            source.lib.utils.daemonize()

    @mock.patch('source.lib.utils.os.fork', mock.Mock(return_value=42))
    def test_daemonize_fork_is_parent(self):
        m__exit = mock.Mock()
        with mock.patch('source.lib.utils.os._exit', m__exit):
            source.lib.utils.daemonize()
        m__exit.assert_called_once_with(0)

    @mock.patch('source.lib.utils.os.fork', mock.Mock(return_value=0))
    @mock.patch('source.lib.utils.os.setsid', mock.Mock())
    def test_daemonize_fork_is_not_parent(self):
        m__exit = mock.Mock()
        with mock.patch('source.lib.utils.os._exit', m__exit):
            source.lib.utils.daemonize()
        self.assertEqual(0, m__exit.call_count)

    @mock.patch('source.lib.utils.os.fork', mock.Mock(side_effect=[0, OSError()]))
    @mock.patch('source.lib.utils.os.setsid', mock.Mock())
    def test_daemonize_fork_is_not_parent_exception(self):
        with self.assertRaises(Exception):
            source.lib.utils.daemonize()

    @mock.patch('source.lib.utils.os.fork', mock.Mock(side_effect=[0, 42]))
    def test_daemonize_fork_fork_is_parent(self):
        m__exit = mock.Mock()
        with mock.patch('source.lib.utils.os._exit', m__exit):
            source.lib.utils.daemonize()
        m__exit.assert_called_once_with(0)

        pass

# daemonize() tests end


# create_pidfile(pidfile_path) tests


class CreatePidfileTestCase(unittest.TestCase):
    @mock.patch('source.lib.utils.os.getpid', mock.Mock(return_value=42))
    def test_create_pidfile_example(self):
        m_open = mock.mock_open()
        with mock.patch('source.lib.utils.open', m_open, create=True):
            source.lib.utils.create_pidfile('/file/path')
        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(42))

    pass

# create_pidfile(pidfile_path) tests end


# load_config_from_pyfile(filepath) tests
cfg_test = {'NYASHMYASH': 'KISABIG',
            'nyashmyash': 'KISASMALL',
            'NYASHMYASh': 'KISASEMIBIG',
            'NYASHMYASH13': 'KISANUMBER',
            '42': 'NOTKISABUTMAYBE',
            '_': 'UNDERKISA',
            'NYASH_MYASH': 'LONGUNDERKISA'}


def fake_execfile(filepath, variables):
    variables.update(cfg_test)


class LoadConfigFromPyfileTestCase(unittest.TestCase):
    @mock.patch('__builtin__.execfile', mock.Mock(side_effect=fake_execfile))
    def test_is_config_set_correctly(self):
        cfg = source.lib.utils.load_config_from_pyfile('')
        self.assertTrue(hasattr(cfg, 'NYASHMYASH'))
        self.assertEqual(cfg.NYASHMYASH, 'KISABIG')
        self.assertTrue(hasattr(cfg, 'NYASHMYASH13'))
        self.assertEqual(cfg.NYASHMYASH13, 'KISANUMBER')
        self.assertTrue(hasattr(cfg, 'NYASH_MYASH'))
        self.assertEqual(cfg.NYASH_MYASH, 'LONGUNDERKISA')
        self.assertFalse(hasattr(cfg, 'nyashmyas'))
        self.assertFalse(hasattr(cfg, 'NYASHMYASh'))
        self.assertFalse(hasattr(cfg, '42'))
        self.assertFalse(hasattr(cfg, '_'))

    pass

# load_config_from_pyfile(filepath) tests end

# parse_cmd_args(args, app_description='') tests


class ParseCmdArgsTestCase(unittest.TestCase):
    def test_set_parser(self):
        with mock.patch('source.lib.utils.argparse.ArgumentParser', mock.Mock()) as m_argparse:
            source.lib.utils.parse_cmd_args([4, 2])
        m_argparse.assert_called_once()

    def test_set_args(self):
        with mock.patch('source.lib.utils.argparse.ArgumentParser.parse_args', mock.Mock()) as m_parse:
            source.lib.utils.parse_cmd_args([4, 2])
        m_parse.assert_called_once([4, 2])
    pass
# parse_cmd_args(args, app_description='') tests end

# get_tube(host, port, space, name) tests


class GetTubeTestCase(unittest.TestCase):
    def test_set_tarantool_queue(self):
        with mock.patch('source.lib.utils.tarantool_queue.Queue.tube', mock.Mock()) as m_tube:
            source.lib.utils.get_tube(42, 42, 42, 'ololo')
            m_tube.assert_called_once_with('ololo')

    def test_get_tube(self):
        with mock.patch('source.lib.utils.tarantool_queue.Queue', mock.Mock()) as m_queue:
            source.lib.utils.get_tube(42, 42, 42, 'ololo')
            m_queue.assert_called_once_with(host=42, port=42, space=42)

    pass
# get_tube(host, port, space, name) tests end

# spawn_workers(num, target, args, parent_pid) tests


class SpawnWorkersTestCase(unittest.TestCase):
    def test_set_process_args(self):
        with mock.patch('source.lib.utils.Process', mock.Mock()) as m_proc:
            source.lib.utils.spawn_workers(1, 42, [4, 2], 42)
            m_proc.assert_called_once_with(target=42, args=[4, 2], kwargs={'parent_pid': 42})

    def test_num_start_processes(self):
        with mock.patch('source.lib.utils.Process.start', mock.Mock()) as m_start:
            source.lib.utils.spawn_workers(42, 42, [4, 2], 42)
        self.assertEqual(m_start.call_count, 42)

    pass
# spawn_workers(num, target, args, parent_pid) tests end

# check_network_status(check_url, timeout) tests


class CheckNetworkStatusTestCase(unittest.TestCase):
    @mock.patch('source.lib.utils.urllib2.urlopen', mock.Mock(side_effect=ValueError()))
    def test_if_value_error(self):
        self.assertFalse(source.lib.utils.check_network_status('ololo.html', 42))

    @mock.patch('source.lib.utils.urllib2.urlopen', mock.Mock(side_effect=urllib2.URLError('ololo')))
    def test_if_urllib_error(self):
        self.assertFalse(source.lib.utils.check_network_status('ololo.html', 42))

    @mock.patch('source.lib.utils.urllib2.urlopen', mock.Mock(side_effect=socket.error()))
    def test_if_socket_error(self):
        self.assertFalse(source.lib.utils.check_network_status('ololo.html', 42))

    def test_set_urlopen_args_correctly(self):
        with mock.patch('source.lib.utils.urllib2.urlopen', mock.Mock()) as m_urlopen:
            source.lib.utils.check_network_status('ololo.html', 42)
            m_urlopen.assert_called_once_with(url='ololo.html', timeout=42)

    @mock.patch('source.lib.utils.urllib2.urlopen', mock.Mock())
    def test_if_ok(self):
        self.assertTrue(source.lib.utils.check_network_status('ololo.html', 42))

    pass
# check_network_status(check_url, timeout) tests end