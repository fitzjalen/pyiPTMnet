from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
  name = 'pyiptmnet',
  packages = ['pyiptmnet'], # this must be the same as the name above
  version = '0.2.0',
  description = 'Python client for iPTMNet REST API - https://research.bioinformatics.udel.edu/iptmnet/',
  long_description = long_description,
  long_description_content_type="text/markdown",
  author = 'Sachn Gavali & Roman Fitzjalen',
  author_email = 'saching@udel.edu & romaactor@gmail.com',
  url = 'https://github.com/fitzjalen/pyiPTMnet', # use the URL to the github repo
  keywords = ['iPTMnet', 'API', 'Client', 'REST-API'], # arbitrary keywords
  classifiers = [],
  install_requires=[
   'certifi',
   'chardet',
   'idna',
   'jsonschema',
   'numpy',
   'pandas',
   'python-dateutil',
   'pytz',
   'requests',
   'six',
   'urllib3'
  ]
)