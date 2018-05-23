try:
    from unittest import mock
except ImportError:
    import mock

from django.test import TestCase

from django_k8s.cache.backends.memcached import (
    get_addresses, AutoDiscoverPyLibMCCache
)
from django_k8s.management.commands.checkmigrations import count_migrations


class AutoDiscoverPyLibMCCacheTestCase(TestCase):
    @mock.patch('django_k8s.cache.backends.memcached.socket.gethostbyname_ex')
    def test_get_addresses(self, mock_gethost):
        mock_gethost.return_value = (
            'foobar.com', [], ['10.1.2.3', '10.1.2.4']
        )

        # Ensure simple host name works.
        addrs = get_addresses(['foobar.com'])
        self.assertEqual(['10.1.2.3', '10.1.2.4'], addrs)

        # Ensure simple address works.
        addrs = get_addresses(['10.1.2.3'])
        self.assertEqual(['10.1.2.3', '10.1.2.4'], addrs)

        # Ensure hostname with port works.
        addrs = get_addresses(['foobar.com:11211'])
        self.assertEqual(['10.1.2.3:11211', '10.1.2.4:11211'], addrs)

        # Ensure address with port works.
        addrs = get_addresses(['10.1.2.3:11211'])
        self.assertEqual(['10.1.2.3:11211', '10.1.2.4:11211'], addrs)

        # Ensure a tuple works.
        addrs = get_addresses([('10.1.2.3', 11211)])
        self.assertEqual(['10.1.2.3:11211', '10.1.2.4:11211'], addrs)

        # Ensure list of host names work.
        addrs = get_addresses(['foobar.com', 'foobaz.com'])
        self.assertEqual(
            [
                '10.1.2.3', '10.1.2.4', '10.1.2.3', '10.1.2.4'
            ],
            addrs)

        # Ensure list of addresses work.
        addrs = get_addresses(['10.1.2.3', '10.1.2.4'])
        self.assertEqual(
            [
                '10.1.2.3', '10.1.2.4', '10.1.2.3', '10.1.2.4'
            ],
            addrs)

    @mock.patch('django_k8s.cache.backends.memcached.socket.gethostbyname_ex')
    def test_cache(self, mock_gethost):
        mock_gethost.return_value = (
            'foobar.com', [], ['10.1.2.3', '10.1.2.4']
        )

        # Ensure our client obtains addresses from DNS.
        cache = AutoDiscoverPyLibMCCache('foobar.com', {})
        self.assertEqual(['10.1.2.3', '10.1.2.4'], cache._cache.addresses)
        self.assertEqual(1, mock_gethost.call_count)

        # Ensure no additonal calls are made for DNS resolution.
        cache._cache
        self.assertEqual(1, mock_gethost.call_count)


class CheckMigrationsTestCase(TestCase):
    def test_count_migrations(self):
        # NOTE: Django test framework applies all migrations before our test.
        # I am not sure how to disable this behavior or even if that is
        # desirable. In any case, migration count is zero.
        nmigrations = count_migrations()
        self.assertEqual(0, nmigrations)