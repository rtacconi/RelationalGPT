# setup.py
from setuptools import setup, find_packages

setup(
    name="relational-gpt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "pytest>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "relational-gpt=relational_gpt.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for LLM-generated relational-functional programming",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/relational-gpt",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)