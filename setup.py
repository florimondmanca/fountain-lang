import re
from pathlib import Path

from setuptools import find_packages, setup


def get_version(package: str) -> str:
    version = (Path("src") / package / "__version__.py").read_text()
    match = re.search("__version__ = ['\"]([^'\"]+)['\"]", version)
    assert match is not None
    return match.group(1)


def get_long_description() -> str:
    with open("README.md", encoding="utf8") as readme:
        return readme.read()


setup(
    name="fountain",
    version=get_version("fountain"),
    description="The Fountain programming language",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="http://github.com/florimondmanca/fountain-lang",
    author="Florimond Manca",
    author_email="florimond.manca@protonmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": "fountain=fountain:main"},
)
