from setuptools import setup

setup(name='hawkular-client-cli',
    version='0.1.0',
    description='Hawkular client cli',
    long_description='Hawkular client command line tool.',
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
        'future',
        'hawkular-client',
    ],
    entry_points={
        'console_scripts': ['hawkular-client-cli=hawkular_client_cli.command_line:main'],
    },
    include_package_data=True,
    zip_safe=False)
