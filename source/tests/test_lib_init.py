import unittest
import source.lib.__init__
import mock
from pycurl import error

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
    @mock.patch('source.lib.__init__.BeautifulSoup')
    def test_not_soup_find(self, BeautifulSoup):
        content = mock.MagicMock()
        url = '1'

        soup = mock.MagicMock()
        soup.find.return_value = False
        BeautifulSoup.return_value = soup

        source.lib.__init__.check_for_meta(content, url)
        soup.find.assert_called_once_with("meta")

    @mock.patch('source.lib.__init__.re.search')
    @mock.patch('source.lib.__init__.urljoin')
    @mock.patch('source.lib.__init__.BeautifulSoup')
    def test_soup_find(self, BeautifulSoup, urljoin, re_search):
        content = mock.MagicMock()
        url = '42'

        attr = mock.MagicMock()
        content_mock = mock.MagicMock()

        soup = mock.MagicMock()
        result = mock.MagicMock()
        wait_mock = mock.MagicMock()
        text_mock = mock.MagicMock()
        text_mock.strip.return_value = text_mock
        result.__getitem__('content').split.return_value = (wait_mock, text_mock)

        result_mock = mock.MagicMock()
        re_search.return_value = result_mock
        result_mock.return_value = ['42']

        return_assert = '42'
        urljoin.return_value = '42'

        result.attrs = {
            'content' : 'content',
            'http-equiv' : 'refresh'
        }

        soup.find.return_value = result
        BeautifulSoup.return_value = soup


        assert  return_assert == source.lib.__init__.check_for_meta(content, url)
        soup.find.assert_called_once_with("meta")
        result.__getitem__('content').split.assert_called_once_with(";")

    @mock.patch('source.lib.__init__.re.search')
    @mock.patch('source.lib.__init__.BeautifulSoup')
    def test_soup_find_re_not_found(self, BeautifulSoup, re_search):
        content = mock.MagicMock()
        url = '42'

        attr = mock.MagicMock()
        content_mock = mock.MagicMock()

        soup = mock.MagicMock()
        result = mock.MagicMock()
        wait_mock = mock.MagicMock()
        text_mock = mock.MagicMock()
        text_mock.strip.return_value = text_mock
        result.__getitem__('content').split.return_value = (wait_mock, text_mock)

        re_search.return_value = False

        result.attrs = {
            'content' : 'content',
            'http-equiv' : 'refresh'
        }

        soup.find.return_value = result
        BeautifulSoup.return_value = soup


        source.lib.__init__.check_for_meta(content, url)
        soup.find.assert_called_once_with("meta")
        result.__getitem__('content').split.assert_called_once_with(";")


    @mock.patch('source.lib.__init__.BeautifulSoup')
    def test_soup_find_len_less_2(self, BeautifulSoup):
        content = mock.MagicMock()
        url = '42'

        attr = mock.MagicMock()
        content_mock = mock.MagicMock()

        soup = mock.MagicMock()
        result = mock.MagicMock()
        result.__getitem__('content').split.return_value = "1"

        result.attrs = {
            'content' : 'content',
            'http-equiv' : 'refresh'
        }

        soup.find.return_value = result
        BeautifulSoup.return_value = soup

        source.lib.__init__.check_for_meta(content, url)
        soup.find.assert_called_once_with("meta")
        result.__getitem__('content').split.assert_called_once_with(";")

    @mock.patch('source.lib.__init__.BeautifulSoup')
    def test_soup_find_attr_not_found(self, BeautifulSoup):
        content = mock.MagicMock()
        url = '42'

        attr = mock.MagicMock()
        content_mock = mock.MagicMock()

        soup = mock.MagicMock()
        result = mock.MagicMock()
        result.__getitem__('content').split.return_value = "1"

        result.attrs = {
            'content' : 'content'
        }

        soup.find.return_value = result
        BeautifulSoup.return_value = soup

        source.lib.__init__.check_for_meta(content, url)
        soup.find.assert_called_once_with("meta")
        assert 0 == result.__getitem__('content').call_count

    pass
# check_for_meta(content, url) tests end


# fix_market_url(url) tests 


class FixMarketUrlTestCase(unittest.TestCase):
    def test_main(self):
        url = mock.MagicMock()
        url.lstrip.return_value = 'yeah'

        result_url = 'http://play.google.com/store/apps/' + 'yeah'

        assert result_url == source.lib.__init__.fix_market_url(url)
        url.lstrip.assert_called_once_with("market://")

    pass 
# fix_market_url(url) tests end


# make_pycurl_request(url, timeout, useragent=None) tests


class MakePycurlRequestTestCase(unittest.TestCase):
    @mock.patch('source.lib.__init__.pycurl')
    @mock.patch('source.lib.__init__.StringIO')
    @mock.patch('source.lib.__init__.to_str')
    @mock.patch('source.lib.__init__.to_unicode')
    def test_all_branch(self, to_unicode, to_str, StringIO, pycurl):
        url = mock.MagicMock()
        timeout = 1
        useragent = mock.Mock()

        curl = mock.MagicMock()
        pycurl.Curl.return_value = curl

        redirect_url = mock.MagicMock() 
        curl.getinfo.return_value = redirect_url
        curl.USERAGENT = '1'

        to_unicode.return_value = '24'

        buff = mock.MagicMock()
        buff.getvalue.return_value = '42'
        StringIO.return_value = buff

        assert ('42', '24') == source.lib.__init__.make_pycurl_request(url, timeout, useragent)
        curl.setopt.assert_any_call('1', useragent)
        curl.close.assert_called_once_with()

    @mock.patch('source.lib.__init__.pycurl')
    @mock.patch('source.lib.__init__.StringIO')
    @mock.patch('source.lib.__init__.to_str')
    def test_not_if_not_if(self, to_str, StringIO, pycurl):
        url = mock.MagicMock()
        timeout = 1

        curl = mock.MagicMock()
        pycurl.Curl.return_value = curl

        redirect_url = None 
        curl.getinfo.return_value = redirect_url

        buff = mock.MagicMock()
        buff.getvalue.return_value = '42'
        StringIO.return_value = buff

        assert ('42', redirect_url) == source.lib.__init__.make_pycurl_request(url, timeout)
        curl.close.assert_called_once_with()

    pass

# make_pycurl_request(url, timeout, useragent=None) tests end


# get_url(url, timeout, user_agent=None) tests
class GetUrlTestCase(unittest.TestCase):
    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(side_effect=['ololo', error()]))
    def test_if_pycurl_error_second(self):
        with mock.patch('source.lib.__init__.logger', mock.Mock()) as m_loger:
            result = source.lib.__init__.get_url('ololo.ru', 42)
            self.assertEqual(1, m_loger.error.call_count)
            self.assertEqual('ololo.ru', result[0])
            self.assertEqual('ERROR', result[1])
            self.assertEqual(None, result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(side_effect=['ololo', ValueError()]))
    def test_if_value_error_second(self):
        with mock.patch('source.lib.__init__.logger', mock.Mock()) as m_loger:
            result = source.lib.__init__.get_url('ololo.ru', 42)
            self.assertEqual(1, m_loger.error.call_count)
            self.assertEqual('ololo.ru', result[0])
            self.assertEqual('ERROR', result[1])
            self.assertEqual(None, result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(side_effect=[ValueError(), 'ololo']))
    def test_if_value_error_first(self):
        with mock.patch('source.lib.__init__.logger', mock.Mock()) as m_loger:
            result = source.lib.__init__.get_url('ololo.ru', 42)
            self.assertEqual(1, m_loger.error.call_count)
            self.assertEqual('ololo.ru', result[0])
            self.assertEqual('ERROR', result[1])
            self.assertEqual(None, result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(side_effect=[error(), 'ololo']))
    def test_if_pycurl_error_first(self):
        with mock.patch('source.lib.__init__.logger', mock.Mock()) as m_loger:
            result = source.lib.__init__.get_url('ololo.ru', 42)
            self.assertEqual(1, m_loger.error.call_count)
            self.assertEqual('ololo.ru', result[0])
            self.assertEqual('ERROR', result[1])
            self.assertEqual(None, result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(return_value=['ish', 'ololo.ru']))
    def test_if_new_redirect_url_and_match(self):
        with (mock.patch('source.lib.__init__.OK_REDIRECT', mock.Mock())):
            with (mock.patch('source.lib.__init__.OK_REDIRECT.match', mock.Mock(return_value=True))):
                result = source.lib.__init__.get_url('vk.ru', 42)
                self.assertEqual(None, result[0])
                self.assertEqual(None, result[1])
                self.assertEqual('ish', result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(return_value=['ish', 'ololo.ru']))
    @mock.patch('source.lib.__init__.check_for_meta', mock.Mock(return_value=None))
    @mock.patch('source.lib.__init__.prepare_url', mock.Mock(return_value=None))
    def test_redirect_url_and_not(self):
        with (mock.patch('source.lib.__init__.OK_REDIRECT', mock.Mock())):
            with (mock.patch('source.lib.__init__.OK_REDIRECT.match', mock.Mock(return_value=False))):
                result = source.lib.__init__.get_url('vk.ru', 42)
                self.assertEqual(None, result[0])
                self.assertEqual(source.lib.__init__.REDIRECT_HTTP, result[1])
                self.assertEqual('ish', result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(return_value=['ish', None]))
    @mock.patch('source.lib.__init__.check_for_meta', mock.Mock(return_value='ololo.ru'))
    @mock.patch('source.lib.__init__.prepare_url', mock.Mock(return_value='vk.com'))
    def test_not_redirect_url_and_redirect_url_and_not_urlsplit(self):
        urlsplit = mock.MagicMock()
        urlsplit.scheme = mock.Mock(return_value='bugaga')
        with (mock.patch('source.lib.__init__.OK_REDIRECT', mock.Mock())):
            with (mock.patch('source.lib.__init__.OK_REDIRECT.match', mock.Mock(return_value=False))):
                result = source.lib.__init__.get_url('vk.ru', 42)
                self.assertEqual(source.lib.__init__.REDIRECT_META, result[1])
                self.assertEqual('ish', result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(return_value=['ish', None]))
    @mock.patch('source.lib.__init__.check_for_meta', mock.Mock(return_value=None))
    @mock.patch('source.lib.__init__.prepare_url', mock.Mock(return_value='vk.com'))
    def test_not_redirect_url_and_not_redirect_url_and_not_urlsplit(self):
        urlsplit = mock.Mock()
        urlsplit.scheme = 'market'
        with (mock.patch('source.lib.__init__.OK_REDIRECT', mock.Mock())):
            with (mock.patch('source.lib.__init__.OK_REDIRECT.match', mock.Mock(return_value=False))):
                with (mock.patch('source.lib.__init__.urlsplit', mock.Mock(return_value=urlsplit))):
                    result = source.lib.__init__.get_url('vk.ru', 42)
                    self.assertEqual(None, result[1])
                    self.assertEqual('ish', result[2])

    @mock.patch('source.lib.__init__.make_pycurl_request', mock.Mock(return_value=['ish', 'ololo']))
    @mock.patch('source.lib.__init__.prepare_url', mock.Mock(return_value='vk.com'))
    def test_redirect_url_and_urlsplit(self):
        urlsplit = mock.Mock()
        urlsplit.scheme = 'market'
        with (mock.patch('source.lib.__init__.OK_REDIRECT', mock.Mock())):
            with (mock.patch('source.lib.__init__.OK_REDIRECT.match', mock.Mock(return_value=False))):
                with (mock.patch('source.lib.__init__.urlsplit', mock.Mock(return_value=urlsplit))):
                    with (mock.patch('source.lib.__init__.fix_market_url', mock.Mock())) as m_fix:
                        result = source.lib.__init__.get_url('vk.ru', 42)
                        self.assertEqual('ish', result[2])
                        self.assertEqual(source.lib.__init__.REDIRECT_HTTP, result[1])
                        self.assertEqual(1, m_fix.call_count)
pass
# get_url(url, timeout, user_agent=None) tests end

# prepare_url(url) tests


class PrepareUrlTestCase(unittest.TestCase):
    @mock.patch('source.lib.__init__.urlparse')
    @mock.patch('source.lib.__init__.urlunparse')
    @mock.patch('source.lib.__init__.quote')
    @mock.patch('source.lib.__init__.quote_plus')
    def test_all_branch(self, quote_plus, quote, urlunparse, urlparse):

        url = mock.MagicMock()

        scheme, netloc, path, qs, anchor, fragments = (
            mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), 
            mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
        )
        urlparse.return_value = (scheme, netloc, path, qs, anchor, fragments)
        urlunparse.return_value = '42'

        netloc.encode.return_value = netloc

        assert '42' == source.lib.__init__.prepare_url(url)

    def test_url_is_none(self):
        url = None
        assert url == source.lib.__init__.prepare_url(url)

    @mock.patch('source.lib.__init__.urlparse')
    @mock.patch('source.lib.__init__.urlunparse')
    @mock.patch('source.lib.__init__.quote')
    @mock.patch('source.lib.__init__.quote_plus')
    def test_exception(self, quote_plus, quote, urlunparse, urlparse):

        url = mock.MagicMock()

        scheme, netloc, path, qs, anchor, fragments = (
            mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), 
            mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
        )
        urlparse.return_value = (scheme, netloc, path, qs, anchor, fragments)
        urlunparse.return_value = '42'

        netloc.encode.side_effect = UnicodeError

        assert '42' == source.lib.__init__.prepare_url(url)

    pass
# prepare_url(url) tests end