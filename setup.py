from setuptools import setup


install_requires = [
    'jsonschema>=3.0.1',
    'networkx==2.6.3',
    'PyYAML>=5.1',
    'requests>=2.26.0',
    'strict-rfc3339>=0.7'
]

extra_requires = [
    'graphviz>=0.19.1'
]

setup(
    name="biothings_schema",
    version="0.1.0",
    author="Jiwen Xin, Chunlei Wu",
    author_email="cwu@scripps.edu",
    description="Python Client for BioThings Schema",
    license="BSD",
    keywords="schema biothings",
    url="https://github.com/biothings/biothings_schema.py",
    packages=['biothings_schema'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=install_requires,
    extras_require={
        'extra': extra_requires
    },
    include_package_data=True
)