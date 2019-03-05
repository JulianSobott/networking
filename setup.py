from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(name='networking',
      version='0.1a4',
      description='High level network communication',
      long_description=long_description,
      url='https://github.com/JulianSobott/networking',
      author='Julian Sobott',
      author_email='julian.sobott@gmx.de',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      keywords='network packet communication',
      project_urls={
        "Bug Tracker": "https://github.com/JulianSobott/networking/issues",
        "Documentation": "https://github.com/JulianSobott/networking/wiki",
        "Source Code": "https://github.com/JulianSobott/networking",
      },
      classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Monitoring",
        ],
      zip_safe=False
      )
