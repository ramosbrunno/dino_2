"""
Testes para o módulo Azure Auth
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sdk.azure_auth import AzureAuth


class TestAzureAuth(unittest.TestCase):
    """Testes para a classe AzureAuth"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.client_id = "12345678-1234-1234-1234-123456789012"
        self.client_secret = "test-client-secret"
        self.tenant_id = "87654321-4321-4321-4321-210987654321"
        
    def test_init(self):
        """Testa a inicialização da classe AzureAuth"""
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        
        self.assertEqual(auth.client_id, self.client_id)
        self.assertEqual(auth.client_secret, self.client_secret)
        self.assertEqual(auth.tenant_id, self.tenant_id)
    
    def test_init_with_empty_client_id(self):
        """Testa inicialização com client_id vazio"""
        with self.assertRaises(ValueError):
            AzureAuth("", self.client_secret, self.tenant_id)
    
    def test_init_with_empty_client_secret(self):
        """Testa inicialização com client_secret vazio"""
        with self.assertRaises(ValueError):
            AzureAuth(self.client_id, "", self.tenant_id)
    
    def test_init_with_empty_tenant_id(self):
        """Testa inicialização com tenant_id vazio"""
        with self.assertRaises(ValueError):
            AzureAuth(self.client_id, self.client_secret, "")
    
    def test_init_with_none_values(self):
        """Testa inicialização com valores None"""
        with self.assertRaises(ValueError):
            AzureAuth(None, self.client_secret, self.tenant_id)
        
        with self.assertRaises(ValueError):
            AzureAuth(self.client_id, None, self.tenant_id)
        
        with self.assertRaises(ValueError):
            AzureAuth(self.client_id, self.client_secret, None)
    
    @patch('sdk.azure_auth.subprocess.run')
    def test_authenticate_success(self, mock_subprocess):
        """Testa autenticação bem-sucedida"""
        # Mock do resultado do subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Login successful"
        mock_subprocess.return_value = mock_result
        
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        result = auth.authenticate()
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once()
        
        # Verificar se o comando correto foi chamado
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("az", call_args)
        self.assertIn("login", call_args)
        self.assertIn("--service-principal", call_args)
    
    @patch('sdk.azure_auth.subprocess.run')
    def test_authenticate_failure(self, mock_subprocess):
        """Testa falha na autenticação"""
        # Mock do resultado do subprocess com erro
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Authentication failed"
        mock_subprocess.return_value = mock_result
        
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        result = auth.authenticate()
        
        self.assertFalse(result)
        mock_subprocess.assert_called_once()
    
    @patch('sdk.azure_auth.subprocess.run')
    def test_authenticate_exception(self, mock_subprocess):
        """Testa exceção durante autenticação"""
        # Mock que lança exceção
        mock_subprocess.side_effect = Exception("Subprocess error")
        
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        result = auth.authenticate()
        
        self.assertFalse(result)
    
    def test_validate_guid_format_valid(self):
        """Testa validação de GUID válido"""
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        
        valid_guids = [
            "12345678-1234-1234-1234-123456789012",
            "87654321-4321-4321-4321-210987654321",
            "ABCDEF12-3456-7890-ABCD-EF1234567890"
        ]
        
        for guid in valid_guids:
            with self.subTest(guid=guid):
                self.assertTrue(auth._validate_guid_format(guid))
    
    def test_validate_guid_format_invalid(self):
        """Testa validação de GUID inválido"""
        auth = AzureAuth(self.client_id, self.client_secret, self.tenant_id)
        
        invalid_guids = [
            "invalid-guid",
            "12345678-1234-1234-1234",  # Muito curto
            "12345678-1234-1234-1234-123456789012-extra",  # Muito longo
            "",  # Vazio
            "12345678-1234-1234-1234-12345678901Z",  # Caractere inválido
        ]
        
        for guid in invalid_guids:
            with self.subTest(guid=guid):
                self.assertFalse(auth._validate_guid_format(guid))


if __name__ == '__main__':
    unittest.main()
