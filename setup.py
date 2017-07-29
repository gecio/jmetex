from setuptools import setup

setup(name='jmetex',
      version='0.1',
      description='Junos Metering Exporter for Prometheus',
      url='http://github.com/innovocloud/jmetex',
      author='Tom Eichhorn',
      author_email='tom.eichhorn@innovo-cloud.de',
      license='Apache',
      packages=['jmetex'],
      entry_points = {
        'console_scripts': ['jmetex=jmetex.main:main'],
      },
      install_requires=[
      'prometheus_client',
      'requests'
      ],
      zip_safe=False)
