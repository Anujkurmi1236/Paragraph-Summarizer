
from setuptools import setup, find_packages

setup(
    name="text-summarizer",
    version="1.0.0",
    description="A floating desktop text summarizer application",
    packages=find_packages(),
    install_requires=[
        "pyperclip>=1.8.2",
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "text-summarizer=summarizer_app:main",
        ],
    },
)