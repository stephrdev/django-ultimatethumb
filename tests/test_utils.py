import os
from unittest import mock

import pytest
from django.core.cache import cache
from django.utils.encoding import force_bytes

from ultimatethumb.utils import (
    MoveableNamedTemporaryFile,
    build_url,
    factor_size,
    get_cache_key,
    get_thumb_data,
    get_thumb_name,
    parse_sizes,
)


def test_get_cache_key():
    assert get_cache_key('test') == 'ultimatethumb:test'


class TestGetThumbName:
    @pytest.fixture(autouse=True)
    def setup(self):
        cache.clear()

    def teardown(self):
        cache.clear()

    def test_call(self):
        assert get_thumb_name('test.jpg', arg1=1, arg2=2) == (
            '207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )

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
    @pytest.fixture(autouse=True)
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
            ['400', '100'],
            ['0', '250'],
            ['50%', '0'],
        ]

    def test_valid_short(self):
        assert parse_sizes('400,250,50%') == [['400', '0'], ['250', '0'], ['50%', '0']]

    def test_valid_mixed(self):
        assert parse_sizes('400x100,250,0x50%') == [['400', '100'], ['250', '0'], ['0', '50%']]

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_sizes('400x100,Ax250')

    def test_invalid_percent(self):
        with pytest.raises(ValueError):
            parse_sizes('5%0x0')

    def test_valid_single_with_viewport(self):
        assert parse_sizes('400x100:600x200') == [['400', '100', '600', '200']]

    def test_valid_multiple_with_viewport(self):
        assert parse_sizes('400x100:300x100,0x250:0x500,50%x0:1000x0') == [
            ['400', '100', '300', '100'],
            ['0', '250', '0', '500'],
            ['50%', '0', '1000', '0'],
        ]

    def test_valid_short_with_viewport(self):
        assert parse_sizes('400:600,250:500,50%:200') == [
            ['400', '0', '600', '0'],
            ['250', '0', '500', '0'],
            ['50%', '0', '200', '0'],
        ]

    def test_valid_mixed_with_viewport(self):
        assert parse_sizes('400x100:600,250,0x50%:200x500') == [
            ['400', '100', '600', '0'],
            ['250', '0'],
            ['0', '50%', '200', '500'],
        ]

    def test_invalid_viewport(self):
        with pytest.raises(ValueError):
            parse_sizes('400x100,Ax250')

    def test_invalid_percent_viewport(self):
        with pytest.raises(ValueError):
            parse_sizes('400:50%x0')


class TestFactorSize:
    def test_int(self):
        assert factor_size(10, 2) == '20'

    def test_string_int(self):
        assert factor_size('10', 2) == '20'

    def test_percent_int(self):
        assert factor_size('10%', 2) == '20%'


class TestBuildUrl:
    def test_no_factor(self):
        assert build_url('207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg') == (
            '/207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )

    def test_with_factor(self):
        assert build_url('207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg', 2) == (
            '/2x/207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )

    def test_domain_with_scheme(self, settings):
        settings.ULTIMATETHUMB_DOMAIN = 'http://statichost'
        assert build_url('207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg') == (
            'http://statichost/207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )

    def test_domain_no_scheme(self, settings):
        settings.ULTIMATETHUMB_DOMAIN = '//statichost'
        assert build_url('207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg') == (
            '//statichost/207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )

    def test_domain_missing_scheme(self, settings):
        settings.ULTIMATETHUMB_DOMAIN = 'statichost'
        assert build_url('207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg') == (
            '//statichost/207736f753aeca1bdbc5ebd4d2e265d45194fc28/test.jpg'
        )


class TestMoveableNamedTemporaryFile:
    def test_init(self):
        tmp = MoveableNamedTemporaryFile('test.jpg')

        assert tmp.name == 'test.jpg'

        # Ensure file rights are set
        assert os.stat(tmp.file.name).st_mode == 33188

    def test_chunks(self):
        tmp = MoveableNamedTemporaryFile('test.jpg')
        tmp.file.write(force_bytes('test123'))
        tmp.file.seek(0)
        assert tmp.chunks() == force_bytes('test123')

    def test_close(self):
        tmp = MoveableNamedTemporaryFile('test.jpg')
        tmp.close()
        assert tmp.file.file.closed is True

    def test_temporary_file_path(self):
        tmp = MoveableNamedTemporaryFile('test.jpg')
        assert tmp.temporary_file_path() == tmp.file.name
        assert tmp.temporary_file_path().endswith('.jpg') is True
