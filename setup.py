#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from ranwinconf import __version__, __author__
from distutils.core import setup

setup(name='ranwinconf',
      version=__version__,
      description='Track changes of the configuration of your windows servers',
      long_description='This tool uses WMI (Windows Management Instrumentation) to collect data on the configuration of the windows servers part of your domain. Resulting files are automatically stored in your CVS or Subversion repository and configuration changes are emailed to you.',
      author=__author__,
      author_email='contact@sebbrochet.com',
      url='https://code.google.com/p/ranwinconf/',
      platforms=['win32'],
      license='MIT License',
      install_requires=['pywin32, WMI'],
      package_dir={ 'ranwinconf': 'lib/ranwinconf' },
      packages=[
         'ranwinconf',
      ],
      scripts=[
         'bin/ranwinconf.py',
         'bin/list_winconf.py'
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: System :: Monitoring',
          ],
      )