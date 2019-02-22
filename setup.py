from setuptools import setup, find_packages

setup(name='networking',
      version='0.1',
      description='High level network communication',
      url='https://github.com/JulianSobott/networking',
      author='Julian Sobott',
      author_email='julian.sobott@gmx.de',
      license='Apache',
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
      zip_safe=False,
      install_requires=['cryptography']
      )
