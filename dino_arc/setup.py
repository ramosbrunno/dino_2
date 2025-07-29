from setuptools import setup, find_packages

setup(
    name='dino_arc',
    version='0.1.0',
    author='Brunno Ramos'
    author_email='brunno.ramos@live.com',
    description='SDK para provisionar recursos no Azure usando Terraform',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'azure-identity',
        'python-terraform',
    ],
    entry_points={
        'console_scripts': [
            'dino_arc=cli:main',
        ],
    },
)