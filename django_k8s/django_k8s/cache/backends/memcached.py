import logging
import socket

from functools import wraps

from django.core.cache.backends.memcached import PyLibMCCache


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def get_addresses(servers):
    "Lookup hostname to determine server address(es)."
    # For each string, try to get the port, perform DNS lookup.
    addresses = []
    for server in servers:
        try:
            host, port = server
        except ValueError:
            try:
                host, port = server.split(':')
                port = int(port)
            except (ValueError, TypeError):
                host, port = server, None

        _, _, addrs = socket.gethostbyname_ex(host)

        for addr in addrs:
            if port is not None:
                addr += ':' + str(port)
            addresses.append(addr)

    # Return a list of strings of "addr[:port]".
    return addresses


def clear_client_on_error(f):
    "Try memcache operation, on failure, clear cache and retry once."
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        for i in range(2):
            try:
                return f(self, *args, **kwargs)
            except:
                if i == 1:
                    raise
                setattr(self, '_client', None)
    return wrapper


class AutoDiscoverPyLibMCCache(PyLibMCCache):
    """
    Handle multiple servers in a single A record.

    Simple auto-discover for use with Kubernetes.
    """

    def __init__(self, server, params):
        super(AutoDiscoverPyLibMCCache, self).__init__(server, params)
        for method_name in ('set', 'set_many', 'get', 'get_many', 'delete'):
            method = getattr(self, method_name)
            setattr(self, method_name, clear_client_on_error(method))

    @property
    def _cache(self):
        this = getattr(self, '_local', self)
        client = getattr(this, '_client', None)

        if client is None:
            client = self._lib.Client(get_addresses(self._servers))

            if self._options:
                client.behaviors = self._options.get(
                    'behaviors', self._options)

            setattr(this, '_client', client)

        return client
