.. image:: https://travis-ci.org/btimby/django-k8s.png
   :target: https://travis-ci.org/btimby/django-k8s
.. image:: https://coveralls.io/repos/github/btimby/django-k8s/badge.svg?branch=master
   :target: https://coveralls.io/github/btimby/django-k8s?branch=master

django-k8s
----------

Integration between Django and Kubernetes.

Caching
=======

Service discovery for Memcached. Admittedly this will work with any service
discovery that uses multiple A records for memcached servers. This allows the
memcached client to properly distribute keys amongst memcached servers. AWS
ElasticCache as well as Kubernetes and others are compatible with this scheme.

If an error is received when trying to access a memcached server, DNS
resolution is performed again (refreshing server list). This allows memcached
servers to be added or removed without restarting the application.

More information on this approach is provided below.

https://cloud.google.com/solutions/deploying-memcached-on-kubernetes-engine

Given Memcached deployed to Kubernetes with the following command:

.. code:: bash

    helm install stable/memcached --name mycache --set replicaCount=3

You could configure your application like this:

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
However Django applications expect the database to be available and migrated on
startup. Therefore some coordination is necessary. The application containers
should wait for the migration job to complete before starting up.

This package provides a management command that polls the database to check for
two conditions:

1. That the database server is reachable.
2. That all migrations have been applied.

It can optionally wait for both of these conditions to be true. An exit code of
``0`` indicates success. This management command could be part of your
entrypoint, ensuring no Django application is started until these conditions
are met.

This technique is compatible with systems other than Kubernetes, the author has
used it with Docker Compose as well.

.. code:: bash

    $ python manage.py checkmigrations
    Migrations complete.
