from setuptools import setup

setup(name='jmetex',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['jmetex'],
      entry_points = {
        'console_scripts': ['jmetex=jmetex.main:main'],
      },
      install_requires=[
      'prometheus_client',
      'requests'
      ],
      zip_safe=False)
