import setuptools
from mysqlite import __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requires = f.read().split()

setuptools.setup(
    name="mysqlite",
    version=__version__,
    author="asteroid_den",
    author_email="denbartolomee@gmail.com",
    description="Minimalistic MySQL and SQLite 3 ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/asteroidden/mysqlite/",
    packages = ['mysqlite'],
    license = 'MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = requires,
    python_requires = '>=3.6',
)
