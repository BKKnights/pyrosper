from setuptools import setup, find_packages

setup(
    name="pyrosper",
    use_scm_version={
        "write_to": "src/pyrosper/version.py",  # This writes a version.py file on build
        "write_to_template": '__version__ = "{version}"\n',
    },
    author="Robert Plummer",
    author_email="robertleeplummerjr@gmail.com",
    description="A continuously improving experimentation framework.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BKKnights/pyrosper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    setup_requires=["setuptools-scm"],
    include_package_data=True,
)
