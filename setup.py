import setuptools
from httpvec.version import __version__

setuptools.setup(
    name='httpvec',
    version=__version__,
    description='Plugin-based HTTP proxy',
    license='MIT',
    author='Mike Haboustak',
    author_email='haboustak@gmail.com',
    url='https://github.com/haboustak/httppvec',
    packages=['httpvec'],
    package_data = {
        'httpvec': [
            'samples/host_header.py',
        ]
    },
    entry_points={
        'console_scripts': [
            'httpvec = httpvec.__main__:main',
        ]
    },
    install_requires = [
        'PyYAML',
    ],
)
