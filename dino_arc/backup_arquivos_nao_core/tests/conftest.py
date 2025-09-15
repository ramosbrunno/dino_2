"""
Configuração de testes para DINO ARC
Inclui fixtures, mocks e utilitários comuns para testes
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
from pathlib import Path

# Adicionar src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_dir():
    """Fixture que cria um diretório temporário para testes"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_azure_credentials():
    """Fixture com credenciais Azure mockadas para testes"""
    return {
        'client_id': 'test-client-id-12345678-1234-1234-1234-123456789abc',
        'client_secret': 'test-client-secret-super-secret-value',
        'tenant_id': 'test-tenant-id-87654321-4321-4321-4321-cba987654321',
        'subscription_id': 'test-subscription-id-abcdef12-3456-7890-abcd-ef1234567890'
    }

@pytest.fixture
def mock_project_config():
    """Fixture com configuração de projeto mockada"""
    return {
        'projeto': 'testapp',
        'ambiente': 'test',
        'location': 'East US',
        'action': 'apply'
    }

@pytest.fixture
def mock_terraform_executable():
    """Mock do executável terraform"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'Terraform v1.5.0'
        mock_run.return_value.stderr = ''
        yield mock_run

@pytest.fixture
def mock_databricks_sdk():
    """Mock do Databricks SDK"""
    with patch('databricks.sdk.WorkspaceClient') as mock_client:
        mock_workspace = Mock()
        mock_workspace.workspace.get_status.return_value = {'state': 'RUNNING'}
        mock_client.return_value = mock_workspace
        yield mock_client

@pytest.fixture
def sample_terraform_output():
    """Fixture com output de exemplo do Terraform"""
    return {
        'resource_group_name': {'value': 'rg-testapp-test'},
        'key_vault_name': {'value': 'kv-testapp-test-abc123'},
        'databricks_workspace_url': {'value': 'https://adb-123456789.12.azuredatabricks.net'},
        'sql_server_name': {'value': 'sql-testapp-test-xyz789'}
    }

@pytest.fixture
def mock_environment_variables():
    """Mock de variáveis de ambiente necessárias"""
    env_vars = {
        'ARM_CLIENT_ID': 'test-client-id',
        'ARM_CLIENT_SECRET': 'test-client-secret',
        'ARM_TENANT_ID': 'test-tenant-id',
        'ARM_SUBSCRIPTION_ID': 'test-subscription-id'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

class MockTerraformResponse:
    """Classe para simular respostas do Terraform"""
    
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

class TestHelpers:
    """Classe com métodos auxiliares para testes"""
    
    @staticmethod
    def create_mock_terraform_file(temp_dir, content="# Mock terraform file"):
        """Cria um arquivo terraform mock para testes"""
        tf_file = Path(temp_dir) / "main.tf"
        tf_file.write_text(content)
        return str(tf_file)
    
    @staticmethod
    def create_mock_config_file(temp_dir, config_data):
        """Cria um arquivo de configuração mock"""
        import json
        config_file = Path(temp_dir) / "config.json"
        config_file.write_text(json.dumps(config_data))
        return str(config_file)
    
    @staticmethod
    def assert_azure_resource_names(resources, projeto, ambiente):
        """Valida nomenclatura padrão dos recursos Azure"""
        expected_patterns = {
            'resource_group': f'rg-{projeto}-{ambiente}',
            'key_vault': f'kv-{projeto}-{ambiente}',
            'sql_server': f'sql-{projeto}-{ambiente}',
            'databricks': f'dbw-{projeto}-{ambiente}'
        }
        
        for resource_type, expected_pattern in expected_patterns.items():
            if resource_type in resources:
                assert expected_pattern in resources[resource_type], \
                    f"Resource {resource_type} não segue padrão esperado {expected_pattern}"
