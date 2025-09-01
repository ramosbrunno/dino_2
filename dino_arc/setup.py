from setuptools import setup, find_packages  
  
setup(  
    name="dino-arc",  
    version="2.0.0",  
    description="DINO ARC - Automated Resource Creator for Azure Databricks with Unity Catalog",  
    packages=find_packages(),  
    install_requires=[  
        "azure-identity",  
        "azure-mgmt-resource",  
        "azure-mgmt-keyvault",  
        "azure-keyvault-secrets",  
        "azure-mgmt-sql",  
        "databricks-sdk",  
        "requests"  
    ],  
    entry_points={  
        "console_scripts": [  
            "dino_arc=dino_arc:main"  
        ]  
    },
    python_requires=">=3.8"  
) 
