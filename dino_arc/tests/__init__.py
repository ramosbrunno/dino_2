"""
Pacote de testes para o projeto Dino ARC

Este pacote contém uma suite completa de testes automatizados para validar
todos os componentes do projeto:

- SDK (Azure Auth, Terraform Executor)
- Configurador Databricks (Unity Catalog)
- CLI e integração
- Validação de arquivos Terraform

Para executar todos os testes:
    python -m tests.test_runner

Para executar testes específicos:
    python -m tests.test_runner --module azure_auth

Para listar módulos disponíveis:
    python -m tests.test_runner --list
"""

__version__ = "1.0.0"
__author__ = "Dino ARC Team"