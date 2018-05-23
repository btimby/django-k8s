.. figure:: https://travis-ci.org/btimby/django-k8s.png
   :alt: Travis CI Status
   :target: https://travis-ci.org/btimby/django-k8s

django-k8s
----------

Integration between Django and Kubernetes.

Caching
=======

Service discovery for Memcache in Kubernetes. This cache backend accepts a
single cache server host name. It performs DNS resolution on this host name and
configures all returned hosts as cache servers.

It can optionally repeat service discovery periodically.

Expects a memcached configuration and implement the approach described below.

https://cloud.google.com/solutions/deploying-memcached-on-kubernetes-engine

Therefore, you configure the backend such as:

.. code:: python

    CACHES = {
        'default': {
            'BACKEND': 'django_k8s.cache.backends.Memcached',
            'HOST': environ.get('DJANGO_CACHE_HOST', None),
        },
    }


Migrations
==========

One convenient way to handle Django migrations in Kubernetes is using a Job.
Django application however expect the database to be available and migrated on
startup. If the database is not migrated the application will error out and
must be restarted. This is not graceful.

A management command is provided that can poll or wait for the configured
database to become available and for the latest migration to be applied.

.. code:: bash

    $ python manage.py checkmigrations
    Migrations complete.

The above will return code ``0`` if the database is available and migrations are
complete or ``1`` if not. The optional ``--wait`` flag will cause the command to
wait until both of these conditions are true.
