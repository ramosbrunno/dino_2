"""
Testes de integração para o Dino SDK
"""

import unittest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSDKIntegration(unittest.TestCase):
    """Testes de integração do SDK completo"""
    
    def test_all_imports(self):
        """Testa se todos os módulos podem ser importados"""
        try:
            from ingestion_engine import IngestionEngine
            from workflow_manager import WorkflowManager
            from genie_assistant import GenieAssistant
            import cli
            
            # Se chegou até aqui, todos os imports funcionaram
            self.assertTrue(True)
            
        except ImportError as e:
            self.fail(f"Falha no import: {str(e)}")
    
    def test_module_instantiation(self):
        """Testa se todas as classes podem ser instanciadas"""
        try:
            from ingestion_engine import IngestionEngine
            from workflow_manager import WorkflowManager
            from genie_assistant import GenieAssistant
            
            # Testar instanciação
            engine = IngestionEngine("test_schema", "test_table")
            workflow = WorkflowManager("test_schema", "test_table")
            genie = GenieAssistant("test_schema", "test_table")
            
            # Verificar se foram criados corretamente
            self.assertIsInstance(engine, IngestionEngine)
            self.assertIsInstance(workflow, WorkflowManager)
            self.assertIsInstance(genie, GenieAssistant)
            
        except Exception as e:
            self.fail(f"Falha na instanciação: {str(e)}")
    
    def test_end_to_end_batch_workflow(self):
        """Testa o fluxo completo para ingestão batch"""
        try:
            from ingestion_engine import IngestionEngine
            from genie_assistant import GenieAssistant
            
            # 1. Criar engine de ingestão
            engine = IngestionEngine("vendas_db", "clientes")
            
            # 2. Executar ingestão batch
            result = engine.execute_ingestion(
                file_path="/tmp/clientes.csv",
                delimiter=",",
                is_automated=False
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['ingestion_type'], 'batch')
            
            # 3. Configurar Genie (opcional)
            genie = GenieAssistant("vendas_db", "clientes")
            genie_result = genie.configure_table_for_genie(
                table_full_name="vendas_db.clientes",
                description="Tabela de clientes"
            )
            
            self.assertTrue(genie_result['success'])
            
        except Exception as e:
            self.fail(f"Falha no fluxo batch: {str(e)}")
    
    def test_end_to_end_streaming_workflow(self):
        """Testa o fluxo completo para ingestão streaming"""
        try:
            from ingestion_engine import IngestionEngine
            from workflow_manager import WorkflowManager
            from genie_assistant import GenieAssistant
            
            # 1. Criar engine de ingestão
            engine = IngestionEngine("vendas_db", "pedidos")
            
            # 2. Executar ingestão streaming
            result = engine.execute_ingestion(
                file_path="/mnt/landing/pedidos/",
                delimiter=",",
                is_automated=True
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['ingestion_type'], 'streaming')
            
            # 3. Criar workflow
            workflow = WorkflowManager("vendas_db", "pedidos")
            workflow_result = workflow.create_auto_ingestion_workflow(
                source_path="/mnt/landing/pedidos/",
                target_table="vendas_db.pedidos",
                checkpoint_location="/mnt/checkpoints/pedidos",
                file_format="csv"
            )
            
            self.assertTrue(workflow_result['success'])
            
            # 4. Configurar Genie
            genie = GenieAssistant("vendas_db", "pedidos")
            genie_result = genie.configure_table_for_genie(
                table_full_name="vendas_db.pedidos",
                description="Tabela de pedidos em tempo real"
            )
            
            self.assertTrue(genie_result['success'])
            
            # Limpar arquivo de workflow se foi criado
            workflow_file = workflow_result.get('workflow_file')
            if workflow_file and os.path.exists(workflow_file):
                os.remove(workflow_file)
            
        except Exception as e:
            self.fail(f"Falha no fluxo streaming: {str(e)}")


if __name__ == '__main__':
    unittest.main()
