# setup.py
from setuptools import setup, find_packages

setup(
    name="CodingAssistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gitpython>=3.1.0",
        "pyyaml>=6.0",
        "networkx>=2.6.0",
        "requests>=2.25.0",
        "tree-sitter>=0.20.0",
    ],
    author="AI Coding Agent Team",
    author_email="example@example.com",
    description="AI agent for coding assistance",
    keywords="ai, coding, assistant",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-coding-agent=CodingAssistant.main:main",
        ],
    },
    include_package_data=True,
)