"""
Testes para o módulo Terraform Executor
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sdk.terraform_executor import TerraformExecutor


class TestTerraformExecutor(unittest.TestCase):
    """Testes para a classe TerraformExecutor"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.executor = TerraformExecutor()
    
    def test_init(self):
        """Testa a inicialização da classe TerraformExecutor"""
        self.assertTrue(hasattr(self.executor, 'working_directory'))
        self.assertIn('terraform', self.executor.working_directory)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_init_success(self, mock_subprocess):
        """Testa terraform init bem-sucedido"""
        # Mock do resultado do subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Terraform has been successfully initialized!"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        result = self.executor.init()
        
        self.assertEqual(result.returncode, 0)
        mock_subprocess.assert_called_once()
        
        # Verificar se o comando correto foi chamado
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args, ["terraform", "init"])
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_init_failure(self, mock_subprocess):
        """Testa falha no terraform init"""
        # Mock do resultado do subprocess com erro
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Failed to initialize"
        mock_subprocess.return_value = mock_result
        
        result = self.executor.init()
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error", result.stderr)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_apply_without_variables(self, mock_subprocess):
        """Testa terraform apply sem variáveis"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = self.executor.apply()
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar comando básico
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args[:3], ["terraform", "apply", "-auto-approve"])
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_apply_with_variables(self, mock_subprocess):
        """Testa terraform apply com variáveis"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        variables = {
            "projeto": "test-project",
            "ambiente": "dev",
            "location": "East US"
        }
        
        result = self.executor.apply(variables=variables)
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar se as variáveis foram incluídas no comando
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("terraform", call_args[0])
        self.assertIn("apply", call_args[1])
        self.assertIn("-auto-approve", call_args[2])
        
        # Verificar se as variáveis estão presentes
        cmd_str = " ".join(call_args)
        self.assertIn("projeto=test-project", cmd_str)
        self.assertIn("ambiente=dev", cmd_str)
        self.assertIn("location=East US", cmd_str)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_apply_with_complex_variables(self, mock_subprocess):
        """Testa terraform apply com variáveis complexas (dict)"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        variables = {
            "projeto": "test-project",
            "tags": {
                "Environment": "dev",
                "Owner": "test-team"
            }
        }
        
        result = self.executor.apply(variables=variables)
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar se o dict foi convertido para JSON
        call_args = mock_subprocess.call_args[0][0]
        cmd_str = " ".join(call_args)
        self.assertIn("projeto=test-project", cmd_str)
        # O dict deve ser convertido para JSON
        self.assertIn("tags=", cmd_str)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_apply_with_var_file(self, mock_subprocess):
        """Testa terraform apply com arquivo de variáveis"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = self.executor.apply(var_file="terraform.tfvars")
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar se o var-file foi incluído
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("-var-file", call_args)
        self.assertIn("terraform.tfvars", call_args)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_plan_success(self, mock_subprocess):
        """Testa terraform plan bem-sucedido"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Plan: 5 to add, 0 to change, 0 to destroy."
        mock_subprocess.return_value = mock_result
        
        variables = {"projeto": "test"}
        result = self.executor.plan(variables=variables)
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar comando
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args[0], "terraform")
        self.assertEqual(call_args[1], "plan")
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_destroy_success(self, mock_subprocess):
        """Testa terraform destroy bem-sucedido"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        variables = {"projeto": "test"}
        result = self.executor.destroy(variables=variables)
        
        self.assertEqual(result.returncode, 0)
        
        # Verificar comando
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args[:3], ["terraform", "destroy", "-auto-approve"])
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_get_outputs_success(self, mock_subprocess):
        """Testa obtenção de outputs bem-sucedida"""
        # Mock de outputs em JSON
        mock_outputs = {
            "databricks_workspace_url": {
                "value": "https://adb-123.azuredatabricks.net"
            },
            "databricks_workspace_id": {
                "value": "123456789"
            }
        }
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_outputs)
        mock_subprocess.return_value = mock_result
        
        result = self.executor.get_outputs()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["databricks_workspace_url"]["value"], "https://adb-123.azuredatabricks.net")
        self.assertEqual(result["databricks_workspace_id"]["value"], "123456789")
        
        # Verificar comando
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args, ["terraform", "output", "-json"])
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_get_outputs_failure(self, mock_subprocess):
        """Testa falha na obtenção de outputs"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: No state file found"
        mock_subprocess.return_value = mock_result
        
        result = self.executor.get_outputs()
        
        self.assertIsNone(result)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_get_outputs_invalid_json(self, mock_subprocess):
        """Testa outputs com JSON inválido"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_subprocess.return_value = mock_result
        
        result = self.executor.get_outputs()
        
        self.assertIsNone(result)
    
    @patch('sdk.terraform_executor.subprocess.run')
    def test_get_outputs_exception(self, mock_subprocess):
        """Testa exceção durante obtenção de outputs"""
        mock_subprocess.side_effect = Exception("Subprocess error")
        
        result = self.executor.get_outputs()
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
