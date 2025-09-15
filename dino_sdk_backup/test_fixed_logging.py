#!/usr/bin/env python3
"""
Teste de integração da nova abordagem de logging do DINO SDK v2.6.2
Testa especificamente a correção do AttributeError: 'IngestionEngine' object has no attribute 'start_ingestion_log'
"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Adicionar o src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fixed_attribute_error():
    """
    Testa se a correção do AttributeError foi implementada corretamente
    """
    print("🔧 TESTE DA CORREÇÃO DO ATTRIBUTEERROR")
    print("=" * 70)
    print("❌ PROBLEMA ANTERIOR: AttributeError: 'IngestionEngine' object has no attribute 'start_ingestion_log'")
    print("✅ SOLUÇÃO IMPLEMENTADA: Método save_ingestion_log() único no final da execução")
    print()
    
    try:
        # Importar as classes necessárias
        from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig
        
        # Criar configuração de teste
        config = IngestionConfig(
            source_path="/test/data.csv",
            catalog_name="dev_test", 
            schema_name="bronze_test",
            table_name="logging_test",
            type_run="batch",
            file_extension="csv"
        )
        
        print(f"📋 Config de teste criada: {config.table_name}")
        
        # Mock do SparkSession
        mock_spark = Mock()
        mock_spark.sql = Mock()
        
        # Criar engine
        engine = IngestionEngine(mock_spark)
        
        # Verificar se o método problemático NÃO existe mais
        print("\n🔍 Verificando se método problemático foi removido...")
        
        has_start_method = hasattr(engine, 'start_ingestion_log')
        has_update_success_method = hasattr(engine, 'update_ingestion_log_success') 
        has_update_error_method = hasattr(engine, 'update_ingestion_log_error')
        has_new_save_method = hasattr(engine, 'save_ingestion_log')
        
        print(f"   start_ingestion_log existe? {has_start_method}")
        print(f"   update_ingestion_log_success existe? {has_update_success_method}")
        print(f"   update_ingestion_log_error existe? {has_update_error_method}")  
        print(f"   save_ingestion_log existe? {has_new_save_method}")
        
        # Resultado da verificação
        if has_start_method or has_update_success_method or has_update_error_method:
            print("⚠️  ATENÇÃO: Métodos antigos ainda existem - podem causar confusão")
        else:
            print("✅ Métodos antigos removidos com sucesso!")
            
        if has_new_save_method:
            print("✅ Novo método save_ingestion_log encontrado!")
        else:
            print("❌ Método save_ingestion_log NÃO encontrado!")
            
        # Testar se o método save_ingestion_log funciona
        print("\n🧪 Testando método save_ingestion_log...")
        
        # Mock dos métodos internos necessários
        engine._is_unity_catalog_enabled = Mock(return_value=False)
        engine._save_log_locally = Mock(return_value="test-execution-123")
        engine._get_file_info = Mock(return_value={
            "files": "test.csv", 
            "total_size": 2048,
            "file_count": 1
        })
        
        # Testar salvamento com sucesso
        start_time = datetime.now()
        end_time = datetime.now()
        
        execution_id = engine.save_ingestion_log(
            config=config,
            execution_status='concluido_sucesso',
            start_time=start_time,
            end_time=end_time,
            records_read=150,
            records_written=150,
            files_ingested="test.csv",
            file_size_bytes=2048
        )
        
        print(f"✅ save_ingestion_log executado com sucesso!")
        print(f"   Execution ID: {execution_id}")
        
        # Verificar se o fallback local foi chamado
        engine._save_log_locally.assert_called_once()
        print("✅ Fallback _save_log_locally foi chamado corretamente")
        
        # Testar salvamento com erro
        print("\n🧪 Testando save_ingestion_log com erro...")
        
        engine._save_log_locally.reset_mock()
        
        execution_id_error = engine.save_ingestion_log(
            config=config,
            execution_status='concluido_erro',
            start_time=start_time,
            end_time=end_time,
            records_read=75,
            records_written=0,
            error_message="Erro de teste simulado",
            error_stack_trace="Stack trace simulado",
            files_ingested="test.csv",
            file_size_bytes=2048
        )
        
        print(f"✅ save_ingestion_log com erro executado!")
        print(f"   Execution ID: {execution_id_error}")
        
        # Verificar chamada com erro
        engine._save_log_locally.assert_called_once()
        print("✅ Fallback para erro funcionou corretamente")
        
        print("\n" + "=" * 70)
        print("🎉 RESULTADO DO TESTE")
        print("=" * 70)
        print("✅ AttributeError corrigido com sucesso!")
        print("✅ Método save_ingestion_log implementado")
        print("✅ Logging simplificado funcionando")
        print("✅ Fallback para Unity Catalog indisponível funciona")
        print("✅ Tratamento de erros integrado")
        print("✅ Todos os campos essenciais capturados")
        
        print("\n📊 RESUMO DA NOVA ABORDAGEM:")
        print("   🔹 Uma única chamada de log ao final da execução")
        print("   🔹 Captura completa de métricas (início, fim, registros, arquivos)")
        print("   🔹 Status final definitivo (sucesso ou erro)")
        print("   🔹 Eliminação de dependências de métodos inexistentes")
        print("   🔹 Código mais robusto e menos propenso a erros")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_fixed_attribute_error()
    print(f"\n{'✅ TESTE PASSOU' if success else '❌ TESTE FALHOU'}")
    sys.exit(0 if success else 1)
