from setuptools import setup, find_packages

setup(
    name="apigee-migrator",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["requests", "pyyaml"],
    entry_points={
        "console_scripts": [
            "apigee-migrator=migrator:main",
        ],
    },
    python_requires=">=3.8",
)
