"""
Testes para o módulo WorkflowManager do Dino SDK
"""

import unittest
import sys
import os
import json

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflow_manager import WorkflowManager


class TestWorkflowManager(unittest.TestCase):
    """Testes para a classe WorkflowManager"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.schema_name = "test_schema"
        self.table_name = "test_table"
        self.workflow_manager = WorkflowManager(self.schema_name, self.table_name)
    
    def test_workflow_manager_initialization(self):
        """Testa a inicialização do WorkflowManager"""
        self.assertEqual(self.workflow_manager.schema_name, self.schema_name)
        self.assertEqual(self.workflow_manager.table_name, self.table_name)
    
    def test_create_auto_ingestion_workflow(self):
        """Testa a criação de workflow de ingestão automatizada"""
        result = self.workflow_manager.create_auto_ingestion_workflow(
            source_path="/mnt/landing/test/",
            target_table=f"{self.schema_name}.{self.table_name}",
            checkpoint_location="/mnt/checkpoints/test",
            file_format="csv",
            delimiter=",",
            max_files_per_trigger=50
        )
        
        self.assertTrue(result['success'])
        self.assertIn('workflow_name', result)
        self.assertIn('workflow_file', result)
        self.assertEqual(result['target_table'], f"{self.schema_name}.{self.table_name}")
        self.assertEqual(result['checkpoint_location'], "/mnt/checkpoints/test")
    
    def test_workflow_name_generation(self):
        """Testa a geração do nome do workflow"""
        result = self.workflow_manager.create_auto_ingestion_workflow(
            source_path="/mnt/landing/test/",
            target_table=f"{self.schema_name}.{self.table_name}",
            checkpoint_location="/mnt/checkpoints/test",
            file_format="csv"
        )
        
        expected_name = f"dino_auto_ingestion_{self.schema_name}_{self.table_name}"
        self.assertEqual(result['workflow_name'], expected_name)
    
    def test_different_file_formats(self):
        """Testa diferentes formatos de arquivo"""
        formats = ["csv", "json", "parquet"]
        
        for file_format in formats:
            with self.subTest(format=file_format):
                result = self.workflow_manager.create_auto_ingestion_workflow(
                    source_path="/mnt/landing/test/",
                    target_table=f"{self.schema_name}.{self.table_name}",
                    checkpoint_location="/mnt/checkpoints/test",
                    file_format=file_format
                )
                
                self.assertTrue(result['success'])
    
    def test_get_workflow_metrics(self):
        """Testa a obtenção de métricas do workflow"""
        metrics = self.workflow_manager.get_workflow_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('status', metrics)
        self.assertIn('total_runs', metrics)
        self.assertIn('successful_runs', metrics)
        self.assertIn('failed_runs', metrics)
    
    def test_workflow_json_structure(self):
        """Testa a estrutura do JSON do workflow gerado"""
        result = self.workflow_manager.create_auto_ingestion_workflow(
            source_path="/mnt/landing/test/",
            target_table=f"{self.schema_name}.{self.table_name}",
            checkpoint_location="/mnt/checkpoints/test",
            file_format="csv"
        )
        
        # Verificar se o arquivo JSON foi criado
        workflow_file = result['workflow_file']
        self.assertTrue(os.path.exists(workflow_file))
        
        # Verificar estrutura do JSON
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_json = json.load(f)
        
        self.assertIn('name', workflow_json)
        self.assertIn('tasks', workflow_json)
        self.assertIn('email_notifications', workflow_json)
        
        # Limpar arquivo de teste
        if os.path.exists(workflow_file):
            os.remove(workflow_file)


if __name__ == '__main__':
    unittest.main()
