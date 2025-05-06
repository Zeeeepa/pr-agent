from setuptools import setup, find_packages

setup(
    name="pr_static_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "jinja2>=3.0.0",
    ],
    author="Codegen",
    author_email="codegen@example.com",
    description="PR Static Analysis Reporting System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zeeeepa/pr-agent",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

