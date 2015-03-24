import mock
import pytest
from django.core.cache import cache

from ultimatethumb.utils import (
    factor_size, get_cache_key, get_thumb_data, get_thumb_name, parse_sizes)


def test_get_cache_key():
    assert get_cache_key('test') == 'ultimatethumb:test'


class TestGetThumbName:
    def setup(self):
        cache.clear()

    def test_call(self):
        assert get_thumb_name('test.jpg', arg1=1, arg2=2) == (
            '207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg')

    def test_call_option_ordering(self):
        result1 = get_thumb_name('test.jpg', arg1=1, arg2=2)
        result2 = get_thumb_name('test.jpg', arg2=2, arg1=1)

        assert result1 == result2

    @mock.patch('ultimatethumb.utils.cache.has_key')
    @mock.patch('ultimatethumb.utils.cache.set')
    def test_call_cache_set(self, set_mock, has_mock):
        has_mock.return_value = False

        result1 = get_thumb_name('test.jpg')
        assert set_mock.call_count == 1

        result2 = get_thumb_name('test.jpg')
        assert set_mock.call_count == 2

        has_mock.return_value = True

        result3 = get_thumb_name('test.jpg')
        assert set_mock.call_count == 2

        assert result1 == result2 == result3


class TestGetThumbData:
    def setup(self):
        cache.clear()

    def test_call_invalid(self):
        with pytest.raises(KeyError):
            get_thumb_data('foobar.jpg')

    def test_call_valid(self):
        result1 = get_thumb_name('test.jpg', arg1=1, arg2=2)
        get_thumb_data(result1)


class TestParseSizes:
    def test_valid_single(self):
        assert parse_sizes('400x100') == [['400', '100']]

    def test_valid_multiple(self):
        assert parse_sizes('400x100,0x250,50%x0') == [
            ['400', '100'], ['0', '250'], ['50%', '0']]

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_sizes('400x100,Ax250')

    def test_invalid_percent(self):
        with pytest.raises(ValueError):
            parse_sizes('5%0x0')


class TestFactorSize:
    def test_int(self):
        assert factor_size(10, 2) == '20'

    def test_string_int(self):
        assert factor_size('10', 2) == '20'

    def test_percent_int(self):
        assert factor_size('10%', 2) == '20%'
