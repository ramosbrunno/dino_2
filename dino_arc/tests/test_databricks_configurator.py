"""
Testes para o configurador do Databricks Unity Catalog
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from databricks_config.unity_catalog_setup import DatabricksConfigurator


class TestDatabricksConfigurator(unittest.TestCase):
    """Testes para a classe DatabricksConfigurator"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.workspace_url = "https://adb-123456789.azuredatabricks.net"
        self.access_token = "dapi1234567890abcdef"
        self.configurator = DatabricksConfigurator(self.workspace_url, self.access_token)
    
    def test_init(self):
        """Testa a inicialização da classe DatabricksConfigurator"""
        self.assertEqual(self.configurator.workspace_url, self.workspace_url)
        self.assertEqual(self.configurator.access_token, self.access_token)
        self.assertIn('Authorization', self.configurator.headers)
        self.assertIn('Bearer', self.configurator.headers['Authorization'])
    
    def test_init_with_trailing_slash(self):
        """Testa inicialização com URL terminando em barra"""
        url_with_slash = "https://adb-123456789.azuredatabricks.net/"
        configurator = DatabricksConfigurator(url_with_slash, self.access_token)
        
        # A URL deve ter a barra removida
        self.assertEqual(configurator.workspace_url, self.workspace_url)
    
    @patch('databricks_config.unity_catalog_setup.requests.get')
    def test_make_request_get(self, mock_get):
        """Testa requisição GET"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        response = self.configurator._make_request('GET', 'test-endpoint')
        
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
    
    @patch('databricks_config.unity_catalog_setup.requests.post')
    def test_make_request_post(self, mock_post):
        """Testa requisição POST"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "created"}
        mock_post.return_value = mock_response
        
        test_data = {"name": "test"}
        response = self.configurator._make_request('POST', 'test-endpoint', test_data)
        
        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        
        # Verificar se os dados foram passados corretamente
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json'], test_data)
    
    @patch('databricks_config.unity_catalog_setup.requests.put')
    def test_make_request_put(self, mock_put):
        """Testa requisição PUT"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        response = self.configurator._make_request('PUT', 'test-endpoint', {"test": "data"})
        
        self.assertEqual(response.status_code, 200)
        mock_put.assert_called_once()
    
    @patch('databricks_config.unity_catalog_setup.requests.delete')
    def test_make_request_delete(self, mock_delete):
        """Testa requisição DELETE"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        response = self.configurator._make_request('DELETE', 'test-endpoint')
        
        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()
    
    def test_make_request_invalid_method(self):
        """Testa método HTTP inválido"""
        with self.assertRaises(ValueError):
            self.configurator._make_request('INVALID', 'test-endpoint')
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_create_unity_catalog_metastore_success(self, mock_request):
        """Testa criação bem-sucedida do metastore"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metastore_id": "test-metastore-id",
            "name": "unity-catalog-east-us"
        }
        mock_request.return_value = mock_response
        
        result = self.configurator.create_unity_catalog_metastore(
            "abfss://container@storage.dfs.core.windows.net/",
            "East US"
        )
        
        self.assertIn("metastore_id", result)
        self.assertEqual(result["metastore_id"], "test-metastore-id")
        mock_request.assert_called_once()
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_create_unity_catalog_metastore_failure(self, mock_request):
        """Testa falha na criação do metastore"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response
        
        result = self.configurator.create_unity_catalog_metastore(
            "abfss://container@storage.dfs.core.windows.net/",
            "East US"
        )
        
        self.assertEqual(result, {})
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_assign_metastore_to_workspace_success(self, mock_request):
        """Testa atribuição bem-sucedida do metastore ao workspace"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = self.configurator.assign_metastore_to_workspace(
            "test-metastore-id",
            "123456789"
        )
        
        self.assertTrue(result)
        mock_request.assert_called_once()
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_assign_metastore_to_workspace_failure(self, mock_request):
        """Testa falha na atribuição do metastore"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Assignment failed"
        mock_request.return_value = mock_response
        
        result = self.configurator.assign_metastore_to_workspace(
            "test-metastore-id",
            "123456789"
        )
        
        self.assertFalse(result)
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_create_catalog_success(self, mock_request):
        """Testa criação bem-sucedida do catalog"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "test_catalog",
            "comment": "Test catalog"
        }
        mock_request.return_value = mock_response
        
        result = self.configurator.create_catalog("test_catalog", "Test catalog")
        
        self.assertIn("name", result)
        self.assertEqual(result["name"], "test_catalog")
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_create_schema_success(self, mock_request):
        """Testa criação bem-sucedida do schema"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "bronze",
            "full_name": "test_catalog.bronze"
        }
        mock_request.return_value = mock_response
        
        result = self.configurator.create_schema("test_catalog", "bronze", "Bronze schema")
        
        self.assertIn("name", result)
        self.assertEqual(result["name"], "bronze")
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_enable_serverless_compute_success(self, mock_request):
        """Testa habilitação bem-sucedida do serverless compute"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = self.configurator.enable_serverless_compute()
        
        self.assertTrue(result)
    
    @patch.object(DatabricksConfigurator, '_make_request')
    def test_create_serverless_warehouse_success(self, mock_request):
        """Testa criação bem-sucedida do SQL warehouse serverless"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "warehouse-123",
            "name": "test-warehouse"
        }
        mock_request.return_value = mock_response
        
        result = self.configurator.create_serverless_warehouse("test-warehouse")
        
        self.assertIn("id", result)
        self.assertEqual(result["id"], "warehouse-123")
    
    @patch.object(DatabricksConfigurator, 'create_unity_catalog_metastore')
    @patch.object(DatabricksConfigurator, 'assign_metastore_to_workspace')
    @patch.object(DatabricksConfigurator, 'create_catalog')
    @patch.object(DatabricksConfigurator, 'create_schema')
    @patch.object(DatabricksConfigurator, 'enable_serverless_compute')
    @patch.object(DatabricksConfigurator, 'create_serverless_warehouse')
    @patch('databricks_config.unity_catalog_setup.time.sleep')
    def test_setup_complete_environment_success(self, mock_sleep, mock_warehouse, 
                                               mock_serverless, mock_schema, mock_catalog,
                                               mock_assign, mock_metastore):
        """Testa configuração completa bem-sucedida do ambiente"""
        # Mock dos retornos de cada método
        mock_metastore.return_value = {"metastore_id": "test-id", "name": "test-metastore"}
        mock_assign.return_value = True
        mock_catalog.return_value = {"name": "test_dev"}
        mock_schema.return_value = {"name": "bronze", "full_name": "test_dev.bronze"}
        mock_serverless.return_value = True
        mock_warehouse.return_value = {"id": "warehouse-123", "name": "test-dev-warehouse"}
        
        result = self.configurator.setup_complete_environment(
            "test", "dev", "abfss://storage/", "East US", "123456789"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("metastore", result)
        self.assertIn("catalog", result)
        self.assertIn("schemas", result)
        self.assertIn("warehouse", result)
        
        # Verificar se todos os métodos foram chamados
        mock_metastore.assert_called_once()
        mock_assign.assert_called_once()
        mock_catalog.assert_called_once()
        mock_serverless.assert_called_once()
        mock_warehouse.assert_called_once()
        
        # Verificar se o schema foi criado 4 vezes (bronze, silver, gold, workspace)
        self.assertEqual(mock_schema.call_count, 4)
    
    @patch.object(DatabricksConfigurator, 'create_unity_catalog_metastore')
    def test_setup_complete_environment_failure(self, mock_metastore):
        """Testa falha na configuração completa do ambiente"""
        # Mock que lança exceção
        mock_metastore.side_effect = Exception("Test error")
        
        result = self.configurator.setup_complete_environment(
            "test", "dev", "abfss://storage/", "East US", "123456789"
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main()
