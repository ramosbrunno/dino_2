"""
Arquivo __init__.py para o pacote de testes
"""

# Versão dos testes
__version__ = "1.0.0"

# Configurações de teste
TEST_CONFIG = {
    'timeout': 300,  # 5 minutos para testes de integração
    'retry_count': 3,
    'azure_regions': ['East US', 'West US 2', 'West Europe'],
    'test_project_prefix': 'dinotest',
    'test_environment': 'test'
}
