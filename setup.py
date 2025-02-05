"""Setup file for Stormtrooper Voice Assistant."""

from setuptools import setup, find_namespace_packages

setup(
    name="trooper",
    version="0.1.0",
    packages=find_namespace_packages(include=["src", "src.*"]),
    package_dir={"": "."},
    install_requires=[
        "boto3",
        "numpy",
        "scipy",
        "soundfile",
        "sounddevice",
        "loguru",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "trooper=src.cli.trooper:main",
        ],
    },
    python_requires=">=3.8",
    description="Stormtrooper Voice Assistant with motion detection and audio effects",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
