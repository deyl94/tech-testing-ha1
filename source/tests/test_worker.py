from sqlite3 import DatabaseError
import unittest
import source.lib.worker
import mock
from tarantool.error import DatabaseError

# def get_redirect_history_from_task(task, timeout, max_redirects=30, user_agent=None) tests


class GetRedirectHistoryFromTaskTestCase(unittest.TestCase):
    @mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=[['ERROR'], 'ololo.ru', []]))
    def test_if_error_and_not_is_recheck(self):
        task = mock.Mock()
        task.data = {'recheck': False,
                     'url': 'ololo.ru',
                     'url_id': 42}
        result = source.lib.worker.get_redirect_history_from_task(
            task, 42, max_redirects=30, user_agent=None)
        self.assertTrue(result[0])
        self.assertTrue(result[1])

    @mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=[['meta_tag'], 'ololo.ru', [4, 2]]))
    def test_if_ok_and_not_suspicious(self):
        task = mock.Mock()
        task.data = {'recheck': True,
                     'url': 'ololo.ru',
                     'url_id': 42}
        result = source.lib.worker.get_redirect_history_from_task(
            task, 42, max_redirects=30, user_agent=None)
        self.assertFalse(result[0])
        self.assertEqual(result[1], {"url_id": 42,
                                     "result": [['meta_tag'], 'ololo.ru', [4, 2]],
                                     "check_type": "normal"})

    @mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=[['meta_tag'], 'ololo.ru', [4, 2]]))
    def test_if_ok_and_suspicious(self):
        task = mock.Mock()
        task.data = {'recheck': True,
                     'url': 'ololo.ru',
                     'url_id': 42,
                     'suspicious': 'sometimes'}
        result = source.lib.worker.get_redirect_history_from_task(
            task, 42, max_redirects=30, user_agent=None)
        self.assertFalse(result[0])
        self.assertEqual(result[1], {"url_id": 42,
                                     "result": [['meta_tag'], 'ololo.ru', [4, 2]],
                                     "check_type": "normal",
                                     "suspicious": 'sometimes'})

    pass


# get_redirect_history_from_task(task, timeout, max_redirects=30, user_agent=None) tests end

# worker(config, parent_pid) tests


class WorkerTestCase(unittest.TestCase):
    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[True, False]))
    @mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=(True, 'ololo')))
    def test_parent_alive_result_and_is_input(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            source.lib.worker.worker(config, 42)
        self.assertTrue(input_tube.put.called)
        self.assertFalse(output_tube.put.called)

    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[True, False]))
    @mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=(False, 'ololo')))
    def test_parent_alive_result_and_not_is_input(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            source.lib.worker.worker(config, 42)
        self.assertFalse(input_tube.put.called)
        self.assertTrue(output_tube.put.called)

    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[True, False]))
    @mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=''))
    def test_parent_alive_not_result(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            source.lib.worker.worker(config, 42)
        self.assertFalse(input_tube.put.called)
        self.assertFalse(output_tube.put.called)

    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[True, False]))
    @mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=(True, 'ololo')))
    def test_task_ask_error(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        task = mock.MagicMock()
        task.ack = mock.Mock(side_effect=DatabaseError)
        input_tube.take = mock.Mock(return_value=task)
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            with mock.patch('source.lib.worker.logger', mock.Mock()) as m_loger:
                source.lib.worker.worker(config, 42)
        self.assertEquals(m_loger.exception.call_count, 1)

    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[True, True, False]))
    def test_if_not_task(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        input_tube.take = mock.Mock(return_value='')
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            with mock.patch('source.lib.worker.logger.info', mock.Mock()) as m_info:
                source.lib.worker.worker(config, 42)
        self.assertEqual(3, m_info.call_count)
        self.assertFalse(input_tube.put.called)
        self.assertFalse(output_tube.put.called)

    @mock.patch('source.lib.worker.os.path.exists', mock.Mock(side_effect=[False]))
    def test_proc_not_exists(self):
        config = mock.MagicMock()
        input_tube = mock.MagicMock()
        output_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[input_tube, output_tube])):
            with mock.patch('source.lib.worker.logger.info', mock.Mock()) as m_info:
                source.lib.worker.worker(config, 42)
        self.assertEqual(3, m_info.call_count)
        self.assertFalse(input_tube.put.called)
        self.assertFalse(output_tube.put.called)


    pass
# worker(config, parent_pid) tests end