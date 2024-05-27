from setuptools import setup, find_packages

setup(
    name="ScreenTime",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "pywin32",
        "tkinter",
        "sqlite3"
    ],
    entry_points={
        "console_scripts": [
            "screentime = screen_time.gui:main",
        ],
    },
    author="Maksim Azarskov",
    author_email="maksim.azarskov@eek.ee",
    description="A simple screen time tracker using Tkinter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mazarskov/ScreenTime",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    python_requires='>=3.10',
)
