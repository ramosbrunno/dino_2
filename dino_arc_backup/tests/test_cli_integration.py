"""
Testes de integração para CLI
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import argparse

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cli import configure_databricks_environment


class TestCLIIntegration(unittest.TestCase):
    """Testes de integração para a CLI"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.projeto = "test-project"
        self.ambiente = "dev"
        self.location = "East US"
    
    @patch('cli.DatabricksConfigurator')
    def test_configure_databricks_environment_success(self, mock_configurator_class):
        """Testa configuração bem-sucedida do Databricks"""
        # Mock do TerraformExecutor
        mock_terraform = MagicMock()
        mock_terraform.get_outputs.return_value = {
            'databricks_workspace_url': {'value': 'https://adb-123.azuredatabricks.net'},
            'databricks_workspace_id': {'value': '123456789'},
            'unity_catalog_storage_root': {'value': 'abfss://storage@account.dfs.core.windows.net/'},
            'databricks_access_token': {'value': 'dapi123456789'}
        }
        
        # Mock do DatabricksConfigurator
        mock_configurator = MagicMock()
        mock_configurator.setup_complete_environment.return_value = {
            'status': 'success',
            'metastore': {'name': 'test-metastore'},
            'catalog': {'name': 'test_dev'},
            'schemas': [{'name': 'bronze'}, {'name': 'silver'}],
            'warehouse': {'name': 'test-dev-warehouse'}
        }
        mock_configurator_class.return_value = mock_configurator
        
        # Executar função
        result = configure_databricks_environment(
            self.projeto, self.ambiente, self.location, mock_terraform
        )
        
        # Verificar resultado
        self.assertTrue(result)
        mock_terraform.get_outputs.assert_called_once()
        mock_configurator_class.assert_called_once()
        mock_configurator.setup_complete_environment.assert_called_once()
    
    @patch('cli.DatabricksConfigurator')
    def test_configure_databricks_environment_no_outputs(self, mock_configurator_class):
        """Testa configuração com outputs do Terraform vazios"""
        # Mock do TerraformExecutor sem outputs
        mock_terraform = MagicMock()
        mock_terraform.get_outputs.return_value = None
        
        # Executar função
        result = configure_databricks_environment(
            self.projeto, self.ambiente, self.location, mock_terraform
        )
        
        # Verificar resultado
        self.assertFalse(result)
        mock_terraform.get_outputs.assert_called_once()
        mock_configurator_class.assert_not_called()
    
    @patch('cli.DatabricksConfigurator')
    def test_configure_databricks_environment_incomplete_outputs(self, mock_configurator_class):
        """Testa configuração com outputs incompletos"""
        # Mock do TerraformExecutor com outputs incompletos
        mock_terraform = MagicMock()
        mock_terraform.get_outputs.return_value = {
            'databricks_workspace_url': {'value': 'https://adb-123.azuredatabricks.net'},
            # Faltando outros outputs necessários
        }
        
        # Executar função
        result = configure_databricks_environment(
            self.projeto, self.ambiente, self.location, mock_terraform
        )
        
        # Verificar resultado
        self.assertFalse(result)
        mock_terraform.get_outputs.assert_called_once()
        mock_configurator_class.assert_not_called()
    
    @patch('cli.DatabricksConfigurator')
    def test_configure_databricks_environment_configurator_failure(self, mock_configurator_class):
        """Testa falha na configuração do Databricks"""
        # Mock do TerraformExecutor
        mock_terraform = MagicMock()
        mock_terraform.get_outputs.return_value = {
            'databricks_workspace_url': {'value': 'https://adb-123.azuredatabricks.net'},
            'databricks_workspace_id': {'value': '123456789'},
            'unity_catalog_storage_root': {'value': 'abfss://storage@account.dfs.core.windows.net/'},
            'databricks_access_token': {'value': 'dapi123456789'}
        }
        
        # Mock do DatabricksConfigurator com falha
        mock_configurator = MagicMock()
        mock_configurator.setup_complete_environment.return_value = {
            'status': 'error',
            'error': 'Configuration failed'
        }
        mock_configurator_class.return_value = mock_configurator
        
        # Executar função
        result = configure_databricks_environment(
            self.projeto, self.ambiente, self.location, mock_terraform
        )
        
        # Verificar resultado
        self.assertFalse(result)
        mock_configurator.setup_complete_environment.assert_called_once()
    
    @patch('cli.DatabricksConfigurator')
    def test_configure_databricks_environment_exception(self, mock_configurator_class):
        """Testa exceção durante configuração"""
        # Mock do TerraformExecutor
        mock_terraform = MagicMock()
        mock_terraform.get_outputs.return_value = {
            'databricks_workspace_url': {'value': 'https://adb-123.azuredatabricks.net'},
            'databricks_workspace_id': {'value': '123456789'},
            'unity_catalog_storage_root': {'value': 'abfss://storage@account.dfs.core.windows.net/'},
            'databricks_access_token': {'value': 'dapi123456789'}
        }
        
        # Mock que lança exceção
        mock_configurator_class.side_effect = Exception("Test exception")
        
        # Executar função
        result = configure_databricks_environment(
            self.projeto, self.ambiente, self.location, mock_terraform
        )
        
        # Verificar resultado
        self.assertFalse(result)


class TestCLIArguments(unittest.TestCase):
    """Testes para validação de argumentos da CLI"""
    
    def test_required_arguments(self):
        """Testa argumentos obrigatórios"""
        required_args = [
            '--client-id', '12345678-1234-1234-1234-123456789012',
            '--client-secret', 'test-secret',
            '--tenant_id', '87654321-4321-4321-4321-210987654321',
            '--action', 'plan',
            '--projeto', 'test-project'
        ]
        
        # Simular parsing de argumentos
        parser = argparse.ArgumentParser()
        parser.add_argument('--client-id', required=True)
        parser.add_argument('--client-secret', required=True)
        parser.add_argument('--tenant_id', required=True)
        parser.add_argument('--action', choices=['init', 'plan', 'apply', 'destroy'], required=True)
        parser.add_argument('--projeto', type=str, required=True)
        parser.add_argument('--ambiente', type=str, choices=['dev', 'staging', 'prod'], default='dev')
        parser.add_argument('--location', type=str, default='East US')
        
        args = parser.parse_args(required_args)
        
        self.assertEqual(args.client_id, '12345678-1234-1234-1234-123456789012')
        self.assertEqual(args.client_secret, 'test-secret')
        self.assertEqual(args.tenant_id, '87654321-4321-4321-4321-210987654321')
        self.assertEqual(args.action, 'plan')
        self.assertEqual(args.projeto, 'test-project')
        self.assertEqual(args.ambiente, 'dev')  # Valor padrão
        self.assertEqual(args.location, 'East US')  # Valor padrão
    
    def test_optional_arguments(self):
        """Testa argumentos opcionais"""
        args_with_optional = [
            '--client-id', '12345678-1234-1234-1234-123456789012',
            '--client-secret', 'test-secret',
            '--tenant_id', '87654321-4321-4321-4321-210987654321',
            '--action', 'apply',
            '--projeto', 'test-project',
            '--ambiente', 'prod',
            '--location', 'West Europe'
        ]
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--client-id', required=True)
        parser.add_argument('--client-secret', required=True)
        parser.add_argument('--tenant_id', required=True)
        parser.add_argument('--action', choices=['init', 'plan', 'apply', 'destroy'], required=True)
        parser.add_argument('--projeto', type=str, required=True)
        parser.add_argument('--ambiente', type=str, choices=['dev', 'staging', 'prod'], default='dev')
        parser.add_argument('--location', type=str, default='East US')
        
        args = parser.parse_args(args_with_optional)
        
        self.assertEqual(args.ambiente, 'prod')
        self.assertEqual(args.location, 'West Europe')
    
    def test_invalid_environment(self):
        """Testa ambiente inválido"""
        invalid_args = [
            '--client-id', '12345678-1234-1234-1234-123456789012',
            '--client-secret', 'test-secret',
            '--tenant_id', '87654321-4321-4321-4321-210987654321',
            '--action', 'apply',
            '--projeto', 'test-project',
            '--ambiente', 'invalid-env'
        ]
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--client-id', required=True)
        parser.add_argument('--client-secret', required=True)
        parser.add_argument('--tenant_id', required=True)
        parser.add_argument('--action', choices=['init', 'plan', 'apply', 'destroy'], required=True)
        parser.add_argument('--projeto', type=str, required=True)
        parser.add_argument('--ambiente', type=str, choices=['dev', 'staging', 'prod'], default='dev')
        
        with self.assertRaises(SystemExit):
            parser.parse_args(invalid_args)
    
    def test_invalid_action(self):
        """Testa ação inválida"""
        invalid_args = [
            '--client-id', '12345678-1234-1234-1234-123456789012',
            '--client-secret', 'test-secret',
            '--tenant_id', '87654321-4321-4321-4321-210987654321',
            '--action', 'invalid-action',
            '--projeto', 'test-project'
        ]
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--client-id', required=True)
        parser.add_argument('--client-secret', required=True)
        parser.add_argument('--tenant_id', required=True)
        parser.add_argument('--action', choices=['init', 'plan', 'apply', 'destroy'], required=True)
        parser.add_argument('--projeto', type=str, required=True)
        
        with self.assertRaises(SystemExit):
            parser.parse_args(invalid_args)


if __name__ == '__main__':
    unittest.main()
