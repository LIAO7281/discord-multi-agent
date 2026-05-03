#!/usr/bin/env python3
"""
Setup script for Discord Multi-Agent Support System.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discord-multi-agent",
    version="1.0.0",
    author="AI Builder",
    author_email="your-email@example.com",
    description="A multi-agent Discord support system based on Hermes Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/discord-multi-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "discord.py>=2.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
        ],
        "advanced": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "pymupdf>=1.23.0",
            "langdetect>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    entry_points={
        "console_scripts": [
            "discord-multi-agent=bot:main",
        ],
    },
)
