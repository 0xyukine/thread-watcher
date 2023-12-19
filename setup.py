from setuptools import setup, find_packages

setup(
        name='threadwatcher',
        version='0.0.1',
        description='wrapper for the funny four leaf website',
        package_dir={'':'src'},
        install_requires=['requests'],
        zip_safe=False
        )
