# from setuptools import setup, find_packages
#
# setup(
#     name="indoorgml_converter",
#     version="0.1.0",
#     packages=find_packages(where="src"),
#     package_dir={"": "src"},
#     entry_points={
#         "console_scripts": [
#             "indoorgml-convert=indoorgml_converter.cli:main",
#         ],
#     },
#     install_requires=[
#         "geopandas>=0.12",
#         "shapely>=2.0",
#         "matplotlib>=3.0",
#     ],
#     python_requires=">=3.8",
# )

# setup.py
from setuptools import setup, find_packages

setup(
    name="indoorgml_converter",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "indoorgml_converter=indoorgml_converter.cli:main",
        ],
    },
    install_requires=[
        "geopandas",
        "matplotlib",
        "pandas",
        "shapely",
    ],
)