"""
Testes para o módulo GenieAssistant do Dino SDK
"""

import unittest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from genie_assistant import GenieAssistant


class TestGenieAssistant(unittest.TestCase):
    """Testes para a classe GenieAssistant"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.schema_name = "test_schema"
        self.table_name = "test_table"
        self.genie = GenieAssistant(self.schema_name, self.table_name)
    
    def test_genie_initialization(self):
        """Testa a inicialização do GenieAssistant"""
        self.assertEqual(self.genie.schema_name, self.schema_name)
        self.assertEqual(self.genie.table_name, self.table_name)
    
    def test_configure_table_for_genie(self):
        """Testa a configuração da tabela para o Genie"""
        table_full_name = f"{self.schema_name}.{self.table_name}"
        description = "Tabela de teste para o Genie Assistant"
        
        result = self.genie.configure_table_for_genie(
            table_full_name=table_full_name,
            description=description
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['table_name'], table_full_name)
        self.assertIn('config_file', result)
    
    def test_get_genie_configuration(self):
        """Testa a obtenção da configuração do Genie"""
        table_full_name = f"{self.schema_name}.{self.table_name}"
        
        # Primeiro configurar
        self.genie.configure_table_for_genie(
            table_full_name=table_full_name,
            description="Tabela de teste"
        )
        
        # Depois obter configuração
        config = self.genie.get_genie_configuration(table_full_name)
        
        self.assertIsInstance(config, dict)
        self.assertIn('success', config)
    
    def test_different_descriptions(self):
        """Testa diferentes descrições de tabela"""
        descriptions = [
            "Tabela de clientes com dados demográficos",
            "Dados de vendas consolidados por período",
            "Informações de produtos e categorias"
        ]
        
        table_full_name = f"{self.schema_name}.{self.table_name}"
        
        for desc in descriptions:
            with self.subTest(description=desc):
                result = self.genie.configure_table_for_genie(
                    table_full_name=table_full_name,
                    description=desc
                )
                
                self.assertTrue(result['success'])
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        # Testar com nome de tabela inválido
        result = self.genie.configure_table_for_genie(
            table_full_name="",  # Nome vazio
            description="Descrição teste"
        )
        
        # Deve retornar erro ou lidar graciosamente
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)


if __name__ == '__main__':
    unittest.main()
