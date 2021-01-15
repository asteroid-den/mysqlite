import setuptools
from mysqlite import __version__

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "mysqlite",
    version = __version__,
    author = "asteroid_den",
    author_email = "denbartolomee@gmail.com",
    description = "Minimalistic MySQL and SQLite 3 ORM",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://bitbucket.org/asteroid_den/mysqlite/",
    packages = ['mysqlite'],
    license = 'MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
)
