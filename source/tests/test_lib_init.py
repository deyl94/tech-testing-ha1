import unittest
import source.lib.__init__
import mock

# to_unicode(val, errors='strict') tests


class ToUnicodeTestCase(unittest.TestCase):
    def test_usuall_string(self):
        self.assertTrue(isinstance(source.lib.__init__.to_unicode('ololo'), unicode))

    def test_unicode_string(self):
        self.assertTrue(isinstance(source.lib.__init__.to_unicode(u'ololo'), unicode))

    def test_number(self):
        self.assertTrue(isinstance(source.lib.__init__.to_unicode(123), unicode))

    pass
# to_unicode(val, errors='strict') tests end

# to_str(val, errors='strict') tests


class ToStrTestCase(unittest.TestCase):
    def test_usuall_string(self):
        self.assertTrue(isinstance(source.lib.__init__.to_str('ololo'), str))

    def test_unicode_string(self):
        self.assertTrue(isinstance(source.lib.__init__.to_str(u'ololo'), str))

    def test_number(self):
        self.assertTrue(isinstance(source.lib.__init__.to_str(123), str))

    pass
# to_str(val, errors='strict') tests

# get_counters(content) tests


class GetCountersTestCase(unittest.TestCase):
    @mock.patch('source.lib.__init__.re.match', mock.Mock(return_value=False))
    def test_not_append_counters(self):
        result = source.lib.__init__.get_counters('')
        self.assertEqual(len(result), 0)

    @mock.patch('source.lib.__init__.re.match', mock.Mock(return_value=True))
    def test_not_append_counters(self):
        result = source.lib.__init__.get_counters('ololo')
        self.assertTrue(len(result) > 0)

    def test_with_regexp(self):
         self.assertEquals(1, len(source.lib.__init__.get_counters('http://google-analytics.com/ga.js')))

    pass
# get_counters(content) tests end

# check_for_meta(content, url) tests


class CheckForMetaTestCase(unittest.TestCase):

    pass
# check_for_meta(content, url) tests end