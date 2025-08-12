"""
Testes para o módulo IngestionEngine do Dino SDK
"""

import unittest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion_engine import IngestionEngine


class TestIngestionEngine(unittest.TestCase):
    """Testes para a classe IngestionEngine"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.schema_name = "test_schema"
        self.table_name = "test_table"
        self.engine = IngestionEngine(self.schema_name, self.table_name)
    
    def test_engine_initialization(self):
        """Testa a inicialização do IngestionEngine"""
        self.assertEqual(self.engine.schema_name, self.schema_name)
        self.assertEqual(self.engine.table_name, self.table_name)
        self.assertEqual(self.engine.table_full_name, f"{self.schema_name}.{self.table_name}")
    
    def test_batch_ingestion(self):
        """Testa a geração de código para ingestão batch"""
        result = self.engine.execute_ingestion(
            file_path="/tmp/test.csv",
            delimiter=",",
            is_automated=False  # Modo batch
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['ingestion_type'], 'batch')
        self.assertEqual(result['table_full_name'], f"{self.schema_name}.{self.table_name}")
        self.assertIn('python_code', result)
    
    def test_streaming_ingestion(self):
        """Testa a geração de código para ingestão streaming"""
        result = self.engine.execute_ingestion(
            file_path="/mnt/landing/test/",
            delimiter=",",
            is_automated=True  # Modo streaming
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['ingestion_type'], 'streaming')
        self.assertEqual(result['table_full_name'], f"{self.schema_name}.{self.table_name}")
        self.assertIn('python_code', result)
    
    def test_different_delimiters(self):
        """Testa diferentes delimitadores"""
        # Teste com ponto e vírgula
        result = self.engine.execute_ingestion(
            file_path="/tmp/test.csv",
            delimiter=";",
            is_automated=False
        )
        
        self.assertTrue(result['success'])
        self.assertIn('";"', result['python_code'])
        
        # Teste com pipe
        result = self.engine.execute_ingestion(
            file_path="/tmp/test.csv",
            delimiter="|",
            is_automated=False
        )
        
        self.assertTrue(result['success'])
        self.assertIn('"|"', result['python_code'])
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        # Testar com parâmetros inválidos
        result = self.engine.execute_ingestion(
            file_path="",  # Caminho vazio
            delimiter=",",
            is_automated=False
        )
        
        # Deve retornar erro ou lidar graciosamente
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)


if __name__ == '__main__':
    unittest.main()
