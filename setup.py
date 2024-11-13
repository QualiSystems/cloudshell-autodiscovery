from setuptools import find_packages, setup

with open("version.txt") as version_file:
    version_from_file = version_file.read().strip()


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


setup(
    name="cloudshell-autodiscovery",
    url="http://www.qualisystems.com",
    author="Quali",
    author_email="info@quali.com",
    version=version_from_file,
    description="",
    long_description=get_file_content("README.md"),
    tests_require=get_file_content("test_requirements.txt"),
    python_requires=">=3.9",
    test_suite="tests",
    packages=find_packages() + ["examples", "data", "json_schemes"],
    include_package_data=True,
    install_requires=get_file_content("requirements.txt"),
    license="Apache Software License 2.0",
    entry_points={"console_scripts": ["autodiscovery=autodiscovery.cli:cli"]},
)
