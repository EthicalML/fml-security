from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="example_project",
    version="0.1.0",
    url="https://github.com/MyGithubUsername/example_project.git",
    author="MyGithubUsername",
    author_email="",
    description="A short description of the project.",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "mlserver==1.1.0.dev6",
    ],
    long_description=Path("README.md").read_text(),
    license="MIT",
)

