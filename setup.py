from distutils.core import setup

setup(name='pyFaultLocUnittest',
      version='0.1',
      description='Fault Localization with unittest',
      author='Tam Yiu Chau',
      author_email='tamyiuchau@gmail.com',
      url='https://github.com/tamyiuchau/pyFaultLocUnittest',
      packages=['faultLoc'],
      package_dir = {'faultLoc': 'bin'}
     )
