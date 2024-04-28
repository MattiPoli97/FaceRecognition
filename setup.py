# setup.py
from setuptools import setup

setup(
    name="face_rec",
    version="1.0",
    description="Face Recognition toolkit",
    author="",
    author_email="",
    url="",
    package_dir={"": "src"},
    packages=["face_rec"],
    scripts=[],
    install_requires=[
        "numpy",
        "opencv-contrib-python",
        "opencv-python",
        "pathlib",
        "setuptools",
        "pillow",
        "click",
        "pygame",
        "pandas",
        "openpyxl",
        "pyttsx3",
    ],
    entry_points={
        "console_scripts": ["face_rec=face_rec.cli:cli"]
    },
)
