import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="serverless_api_authorizer",
    version="0.0.1",

    description="serverless api authorizer",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "premium_api"},
    packages=setuptools.find_packages(where="premium_api"),

    install_requires=[
        "aws-cdk.core==1.47",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
