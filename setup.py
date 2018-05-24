"""django-k8s"""
import os

from os.path import join as pathjoin
from os.path import dirname
from subprocess import check_output, CalledProcessError
from setuptools import find_packages
from setuptools import setup


package_name = 'django-k8s'
version_msg = '# Do not edit. See setup.py.{nl}__version__ = "{ver}"{nl}'
version_py = pathjoin(
    dirname(__file__), package_name.replace('-', '_'), 'version.py')

# Get version from GIT or version.py.
try:
    version_git = check_output(['git', 'describe', '--tags']).rstrip()
    version_git = version_git.decode('utf-8')
except (CalledProcessError, OSError):
    with open(version_py, 'rt') as f:
        version_git = f.read().strip().split('=')[-1].replace('"', '')
else:
    # Write out version.py.
    with open(version_py, 'wt') as f:
        f.write(version_msg.format(ver=version_git, nl=os.linesep))

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme) as readme_file:
    long_description = readme_file.read()


setup(
    name = package_name,
    version = version_git,
    description = 'Integration between Django and Kubernetes.',
    long_description = long_description,
    author = 'Ben Timby',
    author_email = 'btimby@gmail.com',
    url = 'http://github.com/btimby/' + package_name + '/',
    license = 'MIT',
    packages = [
        "django_k8s",
    ],
    classifiers = (
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)