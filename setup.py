from setuptools import find_packages, setup


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


setup(
    name="cloudshell-autodiscovery",
    url="http://www.qualisystems.com",
    author="Quali",
    author_email="anton.p@qualisystems.com",
    version="2.0.0",
    description="",
    long_description=get_file_content("README.md"),
    tests_require=get_file_content("test_requirements.txt"),
    test_suite="nose.collector",
    packages=find_packages() + ["examples", "data", "json_schemes"],
    include_package_data=True,
    install_requires=get_file_content("requirements.txt"),
    license="Apache Software License 2.0",
    entry_points={"console_scripts": ["autodiscovery=autodiscovery.cli:cli"]},
)
