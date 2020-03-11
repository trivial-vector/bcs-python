from setuptools import find_packages, setup


setup(
    name="Bootcampspot-python",
    version="0.0.1",
    author="Justin Parker",
    author_email="justin.parker.12@gmail.com",
    description=("Python wrapper for Bootcampspot API"),
    license="MIT",
    keywords="Bootcampspot API Wrapper",
    url="https://github.com/Ouroboros-analytics/bcs-python",
    packages=find_packages("."),
    long_description="",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
