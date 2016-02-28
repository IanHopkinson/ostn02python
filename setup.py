from setuptools import setup, find_packages

long_desc = """
OSTN02 coordinate conversion utility 
"""
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers


conf = dict(
    name='osn02python',
    version='1.0.0',
    description="OSTN02 coordinate conversion utility",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "License :: Free To Use But Restricted",
    ],
    keywords='',
    author='Tim Sheerman-Chase',
    author_email='tim2009@sheerman-chase.org.uk',
    url='http://www.sheerman-chase.org.uk',
    license='Free To Use But Restricted',
    packages=["ostn02python"],
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[],
    tests_require=[],
    entry_points={}
    )

if __name__ == '__main__':
    setup(**conf)