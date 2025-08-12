from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name='dino-arc',
    version='1.0.0',
    author='Brunno Ramos',
    author_email='brunno.ramos@live.com',
    description='Dino ARC - Azure Resource Creator: CLI para provisionar infraestrutura Azure completa com Databricks Premium e Unity Catalog',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ramosbrunno/dino_2",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'dino-arc=cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'terraform': ['*.tf', '*.tfvars.example', '*.gitignore'],
        'terraform.modules.foundation': ['*.tf'],
        'terraform.modules.databricks': ['*.tf'],
    },
    keywords=[
        'azure', 'terraform', 'infrastructure', 'databricks', 'unity-catalog',
        'cli', 'automation', 'cloud', 'iac', 'infrastructure-as-code'
    ],
)