"""
DINO SDK v2.5.1 - Exemplo de Sistema de Logging Robusto
=======================================================

Este exemplo demonstra o sistema de logging abrangente com fallback automático
para ambientes com e sem Unity Catalog.
"""

import logging
from datetime import datetime
from dino_sdk.ingestion_engine import IngestionEngine
from dino_sdk.workflow_manager import IngestionConfig

# Configurar logging para ver os logs locais
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def exemplo_ingestao_com_logging():
    """
    Exemplo completo de ingestão com sistema de logging robusto.
    """
    
    print("🚀 DINO SDK v2.5.1 - Sistema de Logging Abrangente")
    print("=" * 60)
    
    # Inicializar engine
    engine = IngestionEngine()
    print(f"✅ Engine inicializado")
    
    # Verificar ambiente
    uc_enabled = engine._is_unity_catalog_enabled()
    print(f"🔍 Unity Catalog: {'Habilitado' if uc_enabled else 'Não habilitado'}")
    
    if uc_enabled:
        print("📊 Logs serão salvos na tabela Delta")
    else:
        print("📋 Logs serão exibidos no console com estrutura completa")
    
    print("-" * 60)
    
    # Configuração de ingestão
    config = IngestionConfig(
        catalog_name="dev_catalog",
        schema_name="bronze_layer", 
        table_name="vendas_exemplo",
        source_path="/path/to/data/vendas.csv",
        file_extension="csv",
        file_delimiter=",",
        file_header=True,
        type_run="full_load",
        multiline=False,
        schema_evolution_mode="addNewColumns"
    )
    
    print(f"📁 Configuração criada:")
    print(f"   - Tabela: {config.catalog_name}.{config.schema_name}.{config.table_name}")
    print(f"   - Fonte: {config.source_path}")
    print(f"   - Tipo: {config.type_run}")
    
    # Construir path de destino seguro
    safe_path = engine._build_safe_destination_path(config)
    print(f"   - Destino: {safe_path}")
    
    print("-" * 60)
    
    # Demonstrar logging de início
    print("🔍 Iniciando log de execução...")
    execution_id = engine.start_ingestion_log(config)
    print(f"✅ Execution ID: {execution_id}")
    
    # Simular início da ingestão
    start_time = datetime.now()
    print(f"⏱️  Início da execução: {start_time.strftime('%H:%M:%S')}")
    
    try:
        # Simular processamento (substitua pela sua lógica real)
        print("⚙️  Processando dados...")
        
        # Simular leitura de dados
        records_read = 1500
        print(f"📖 Registros lidos: {records_read}")
        
        # Simular processamento
        import time
        time.sleep(2)  # Simular tempo de processamento
        
        # Simular escrita de dados
        records_written = 1450
        print(f"📝 Registros escritos: {records_written}")
        
        # Log de sucesso
        print("✅ Atualizando log com sucesso...")
        engine.update_ingestion_log_success(
            execution_id=execution_id,
            config=config,
            records_read=records_read,
            records_written=records_written,
            start_time=start_time
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"🎉 Ingestão concluída com sucesso!")
        print(f"   - Duração: {duration:.2f} segundos")
        print(f"   - Taxa de sucesso: {(records_written/records_read)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Erro durante ingestão: {str(e)}")
        
        # Simular stack trace
        import traceback
        stack_trace = traceback.format_exc()
        
        # Log de erro
        print("❌ Atualizando log com erro...")
        engine.update_ingestion_log_error(
            execution_id=execution_id,
            config=config,
            error_message=str(e),
            error_stack_trace=stack_trace,
            start_time=start_time
        )
        
        print("🔍 Detalhes do erro logados")
    
    print("-" * 60)
    
    if uc_enabled:
        print("📊 Para consultar logs na tabela Delta:")
        print(f"   SELECT * FROM {config.catalog_name}.{config.schema_name}.ingestion_logs")
        print(f"   WHERE execution_id = '{execution_id}'")
    else:
        print("📋 Logs estruturados foram exibidos no console acima")
        print("   Em produção, configure um sistema de coleta de logs")
    
    print("\n🎯 Sistema de logging funcionando corretamente!")
    return execution_id

def exemplo_deteccao_ambiente():
    """
    Demonstra a detecção automática de ambiente.
    """
    print("\n🔍 Detecção Automática de Ambiente")
    print("=" * 40)
    
    engine = IngestionEngine()
    
    # Testar detecção de Unity Catalog
    try:
        uc_enabled = engine._is_unity_catalog_enabled()
        if uc_enabled:
            print("✅ Unity Catalog detectado e habilitado")
            print("   - Logs serão salvos em tabelas Delta")
            print("   - Volumes Unity Catalog disponíveis")
            print("   - SQL queries habilitadas")
        else:
            print("⚠️  Unity Catalog não habilitado neste ambiente")
            print("   - Usando fallback para logs estruturados")
            print("   - Paths alternativos serão usados")
            print("   - Funcionalidade completa mantida")
    except Exception as e:
        print(f"❌ Erro na detecção: {str(e)}")
    
    # Testar construção de paths
    try:
        from dino_sdk.workflow_manager import IngestionConfig
        
        test_config = IngestionConfig(
            catalog_name="test_catalog",
            schema_name="test_schema", 
            table_name="test_table",
            source_path="/test/path",
            file_extension="parquet"
        )
        
        safe_path = engine._build_safe_destination_path(test_config)
        print(f"\n📁 Path de destino construído: {safe_path}")
        
        if "/Volumes/" in safe_path:
            print("   - Usando Unity Catalog Volumes")
        elif "/mnt/" in safe_path:
            print("   - Usando mount points tradicionais")
        else:
            print("   - Usando DBFS padrão")
            
    except Exception as e:
        print(f"❌ Erro na construção de path: {str(e)}")

if __name__ == "__main__":
    print("🎯 DINO SDK v2.5.1 - Demonstração Completa")
    print("=" * 50)
    
    # Executar detecção de ambiente
    exemplo_deteccao_ambiente()
    
    # Executar exemplo completo
    execution_id = exemplo_ingestao_com_logging()
    
    print(f"\n📋 Execution ID gerado: {execution_id}")
    print("✅ Demonstração concluída!")
