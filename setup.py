from setuptools import setup, find_packages


def requirements():
    reqs = []
    with open("requirements.txt") as f:
        for line in f.readlines():
            reqs.append(line)
    return reqs


def description():
    with open("README.md") as f:
        return f.read()

setup(
    name="tenantpy",
    version="1.0.5",
    author="zhouhao",
    python_requires='>=3.7.0',
    author_email="zhouhao19931002@hotmail.com",
    long_description=description(),
    long_description_content_type="text/markdown",
    maintainer="zhouhao",
    description="Tenant Management For Web Application",
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7"
    ]
)
