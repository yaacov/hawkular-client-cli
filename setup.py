from setuptools import setup

_VERSION = '0.13.2'
_DESCRIPTION = 'Read/Write data to and from a Hawkular metric server.'

setup(name='hawkular-client-cli',
    version=_VERSION,
    description='Hawkular client cli',
    long_description=_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Monitoring',
    ],
    url='http://github.com/yaacov/hawkular-client-cli',
    author='Yaacov Zamir',
    author_email='yzamir@redhat.com',
    license='Apache License 2.0',
    packages=['hawkular_client_cli'],
    install_requires=[
        'future>=0.15.0',
        'python-dateutil>=2.0.0',
        'PyYAML>=3.0',
        'hawkular-client>=0.1.0',
    ],
    entry_points={
        'console_scripts': ['hawkular-client-cli=hawkular_client_cli.command_line:main'],
    },
    include_package_data=True,
    zip_safe=False)
