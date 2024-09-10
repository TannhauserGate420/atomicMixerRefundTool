#!/usr/bin/env python3

from setuptools import (
    setup,
    find_packages
)

with open(f"README.md", "r", encoding="utf-8") as readme:
    long_description: str = readme.read()

setup(
    name = "atomicmixer",
    version = "0.1.3",
    description = "AtomicMixerRefundTool",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "iizegrim",
    author_email = "iizegrim@protonmail.com",
    url = "https://github.com/TannhauserGate420/atomicMixerRefundTool",
    keywords = [
        "atomicmixer",
        "atomicblender",
        "atomicswap",
        "atomic",
        "swap",
        "bitcoin",
        "lightning",
        "cryptocurrencies",
        "cryptocurrency",
        "refund",
        "refundtool"
    ],
    python_requires = ">=3.8, <4",
    packages = find_packages(),
    install_requires = ['python-bitcoinlib',
                    'requests',
                    'emoji',
                    'PyQt5',
                    'fake_http_header',
    ],
    entry_points = {
        "console_scripts": ["atomicmixer = atomicmixer.__main__:main"]
    },
    classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Utilities'
          ],
    include_package_data = True
)
