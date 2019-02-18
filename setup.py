import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="strangenet",
        version="0.0.1",
        author="Aidan Hunt",
        author_email="aidanhunt@acm.org",
        description="IP-over-DigiMesh link layer using TUN",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/aidanh010/strangenet",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
            "Topic :: Internet",
            "Development Status :: 3 - Alpha",
            ],
)
