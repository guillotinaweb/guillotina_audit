# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


test_requires = [
    "async_asgi_testclient",
    "pytest>=8.4.0,<9.0.0",
    "pytest-asyncio>=0.26.0,<1.0.0",
    "pytest-rerunfailures>=16.3,<17.0",
    "coverage",
    "pytest-cov",
    "pytest-docker-fixtures[pg]>=1.3.0",
    "docker>=7.1.0",
]


setup(
    name="guillotina_audit",
    description="elasticsearch audit support for guillotina",
    keywords="search async guillotina elasticsearch audit",
    author="Nil Bacardit Vinyals",
    author_email="n.bacardit@iskra.cat",
    version=open("VERSION").read().strip(),
    long_description=(open("README.rst").read() + "\n" + open("CHANGELOG.rst").read()),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/guillotinaweb/guillotina_audit",
    license="GPL version 3",
    setup_requires=["pytest-runner"],
    zip_safe=True,
    include_package_data=True,
    package_data={"": ["*.txt", "*.rst"], "guillotina_audit": ["py.typed"]},
    packages=find_packages(exclude=["ez_setup"]),
    python_requires=">=3.10",
    install_requires=[
        "guillotina>=7.0.0",
        "pydantic",
        "elasticsearch[async]>=9.0.0,<10.0.0",
    ],
    tests_require=test_requires,
    extras_require={"test": test_requires},
)
