"""
Setup configuration for Dino SDK
Data Ingestion SDK for Databricks with Unity Catalog integration
"""

from setuptools import setup, find_packages
import os

# Ler requirements
def read_requirements():
    # Use requirements mínimos para teste
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements_minimal.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Ler README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Dino SDK - Data Ingestion SDK for Databricks"

setup(
    name="dino-sdk",
    version='2.7.1',
    description='Correção crítica: métodos duplicados removidos, tabela Unity Catalog sempre tenta criar, fallback robusto para logging local',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Data Master Team",
    author_email="support@datamaster.com",
    url="https://github.com/ramosbrunno/dino_2",
    
    # Package discovery - estrutura corrigida para src layout
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include all Python files
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Console scripts - CLI commands (ajustados para src layout)
    entry_points={
        "console_scripts": [
            "dino-ingest=dino_sdk.cli:main",
            "dino-config=dino_sdk.config_cli:config",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Data Processing",
    ],
    
    # Requirements
    python_requires=">=3.8",
    
    # Keywords
    keywords="databricks, data-ingestion, unity-catalog, genie, pyspark, delta-lake",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/ramosbrunno/dino_2/issues",
        "Source": "https://github.com/ramosbrunno/dino_2",
        "Documentation": "https://github.com/ramosbrunno/dino_2/blob/main/README.md",
    },
)
