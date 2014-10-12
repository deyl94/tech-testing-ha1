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
        url.lstrip.assert_called_once_with("market://"); 

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


# make_pycurl_request(url, timeout, useragent=None) tests end


# prepare_url(url) tests

class PrepareUrlTestCase(unittest.TestCase):
    pass
    # @patch('source.lib.__init__.')
    # def test_all_branch(self):
