from distutils.core import setup

setup(
    name='favorites',
    version='0.2',
    description='Generic favorites application for Django',
    author='Andrew Gwozdziewycz',
    author_email='git@apgwoz.com',
    license='LGPL',
    packages=['favorites', 'favorites.templatetags'],
    package_data={
      'favorites': ['templates/favorites/*.html'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
