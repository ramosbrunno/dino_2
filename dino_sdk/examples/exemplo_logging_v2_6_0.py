"""
DINO SDK v2.6.0 - Exemplo de Sistema de Logging Otimizado
=========================================================

Este exemplo demonstra o sistema de logging melhorado com todas as informações
solicitadas: horários, mensagens, arquivos, volumes de dados.
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

def exemplo_ingestao_completa():
    """
    Exemplo de ingestão com sistema de logging otimizado v2.6.0.
    """
    
    print("🚀 DINO SDK v2.6.0 - Sistema de Logging Otimizado")
    print("=" * 60)
    
    # Inicializar engine
    engine = IngestionEngine()
    print(f"✅ Engine inicializado")
    
    # Verificar ambiente
    uc_enabled = engine._is_unity_catalog_enabled()
    print(f"🔍 Unity Catalog: {'Habilitado' if uc_enabled else 'Não habilitado'}")
    
    print("-" * 60)
    
    # Configuração de ingestão
    config = IngestionConfig(
        catalog_name="dev_catalog",
        schema_name="bronze_layer", 
        table_name="vendas_completas",
        source_path="/path/to/data/vendas/*.csv",  # Wildcards suportados
        file_extension="csv",
        file_delimiter=",",
        file_header=True,
        type_run="batch",  # Para demonstrar contagem de registros
        multiline=False,
        schema_evolution_mode="addNewColumns"
    )
    
    print(f"📁 Configuração criada:")
    print(f"   - Tabela: {config.catalog_name}.{config.schema_name}.{config.table_name}")
    print(f"   - Fonte: {config.source_path}")
    print(f"   - Tipo: {config.type_run}")
    
    print("-" * 60)
    
    # Executar ingestão completa
    print("🔍 Executando ingestão completa...")
    try:
        result = engine.ingest(config)
        
        if result.get("success"):
            print("🎉 Ingestão concluída com sucesso!")
            print(f"   - Execution ID: {result.get('execution_id')}")
            print(f"   - Modo: {result.get('mode')}")
            print(f"   - Registros lidos: {result.get('records_read', 'N/A')}")
            print(f"   - Registros gravados: {result.get('records_written', 'N/A')}")
            print(f"   - Duração: {result.get('execution_duration_seconds', 0):.2f}s")
            print(f"   - Mensagem: {result.get('message')}")
        else:
            print("❌ Ingestão falhou")
            print(f"   - Erro: {result.get('error', 'Erro desconhecido')}")
    
    except Exception as e:
        print(f"❌ Erro durante ingestão: {str(e)}")
    
    print("-" * 60)
    
    if uc_enabled:
        print("📊 Para consultar logs detalhados:")
        print(f"""
        -- Último log desta tabela
        SELECT 
            execution_id,
            execution_status,
            start_time,
            end_time,
            execution_duration_seconds,
            records_read,
            records_written,
            message,
            files_ingested,
            file_size_bytes,
            error_message
        FROM {config.catalog_name}.{config.schema_name}.ingestion_logs
        WHERE table_name = '{config.table_name}'
        ORDER BY start_time DESC
        LIMIT 1;
        """)
    else:
        print("📋 Logs estruturados foram exibidos no console acima")
    
    return result.get('execution_id') if result else None

def exemplo_consultas_logs():
    """
    Exemplos de consultas úteis para monitoramento.
    """
    print("\n📊 Exemplos de Consultas de Monitoramento")
    print("=" * 50)
    
    queries = {
        "Últimas execuções com sucesso": """
        SELECT execution_id, table_name, 
               records_read, records_written,
               execution_duration_seconds,
               files_ingested,
               ROUND(file_size_bytes/1024/1024, 2) as file_size_mb
        FROM catalog.schema.ingestion_logs 
        WHERE execution_status = 'concluido_sucesso'
        ORDER BY start_time DESC 
        LIMIT 10;
        """,
        
        "Execuções com erro nas últimas 24h": """
        SELECT execution_id, table_name, 
               message, error_message,
               files_ingested, execution_duration_seconds
        FROM catalog.schema.ingestion_logs 
        WHERE execution_status = 'concluido_erro'
          AND start_time >= current_timestamp() - INTERVAL '24 HOURS'
        ORDER BY start_time DESC;
        """,
        
        "Estatísticas por tabela": """
        SELECT table_name,
               COUNT(*) as total_executions,
               SUM(CASE WHEN execution_status = 'concluido_sucesso' THEN 1 ELSE 0 END) as success_count,
               SUM(CASE WHEN execution_status = 'concluido_erro' THEN 1 ELSE 0 END) as error_count,
               AVG(execution_duration_seconds) as avg_duration_seconds,
               SUM(records_written) as total_records_written
        FROM catalog.schema.ingestion_logs 
        WHERE start_time >= current_timestamp() - INTERVAL '7 DAYS'
        GROUP BY table_name
        ORDER BY total_executions DESC;
        """,
        
        "Performance por arquivo": """
        SELECT files_ingested,
               COUNT(*) as executions,
               AVG(execution_duration_seconds) as avg_duration,
               AVG(file_size_bytes/1024/1024) as avg_file_size_mb,
               AVG(records_read) as avg_records_read
        FROM catalog.schema.ingestion_logs 
        WHERE execution_status = 'concluido_sucesso'
          AND files_ingested IS NOT NULL
        GROUP BY files_ingested
        HAVING COUNT(*) > 1
        ORDER BY avg_duration DESC;
        """
    }
    
    for name, query in queries.items():
        print(f"\n🔍 {name}:")
        print(query)

def demonstrar_estrutura_logs():
    """
    Demonstra a estrutura completa dos logs v2.6.0.
    """
    print("\n📋 Estrutura dos Logs v2.6.0")
    print("=" * 40)
    
    # Simular estrutura de log
    log_example = {
        "execution_id": "550e8400-e29b-41d4-a716-446655440000",
        "table_name": "vendas_completas",
        "schema_name": "bronze_layer",
        "catalog_name": "dev_catalog",
        "source_path": "/path/to/data/vendas/*.csv",
        "execution_status": "concluido_sucesso",
        "start_time": "2025-09-08T10:00:00.000Z",
        "end_time": "2025-09-08T10:02:30.500Z",
        "execution_duration_seconds": 150.5,
        "records_read": 10000,
        "records_written": 9850,
        "file_format": "csv",
        "ingestion_type": "batch",
        "message": "Ingestão concluída com sucesso. 10000 registros lidos, 9850 registros gravados.",
        "error_message": None,
        "error_stack_trace": None,
        "files_ingested": "vendas_jan.csv, vendas_fev.csv, vendas_mar.csv",
        "file_size_bytes": 52428800,  # ~50MB
        "additional_metadata": "{'delimiter': ',', 'header': True, 'unity_catalog_enabled': True}"
    }
    
    print("✅ Exemplo de Log de Sucesso:")
    for key, value in log_example.items():
        print(f"   {key:25}: {value}")
    
    print("\n❌ Exemplo de Log de Erro:")
    error_example = {
        "execution_id": "550e8400-e29b-41d4-a716-446655440001",
        "execution_status": "concluido_erro",
        "message": "Ingestão falhou com erro: Schema validation failed",
        "error_message": "Schema validation failed - column 'data_venda' not found",
        "files_ingested": "dados_incorretos.csv",
        "file_size_bytes": 1048576,
        "execution_duration_seconds": 45.2
    }
    
    for key, value in error_example.items():
        print(f"   {key:25}: {value}")

if __name__ == "__main__":
    print("🎯 DINO SDK v2.6.0 - Demonstração do Sistema de Logging Otimizado")
    print("=" * 70)
    
    # Executar exemplo completo
    execution_id = exemplo_ingestao_completa()
    
    # Mostrar estrutura dos logs
    demonstrar_estrutura_logs()
    
    # Exemplos de consultas
    exemplo_consultas_logs()
    
    print(f"\n📋 Execution ID gerado: {execution_id}")
    print("\n🎉 Principais Melhorias v2.6.0:")
    print("   ✅ Removido destination_path (redundante)")
    print("   ✅ Campo execution_status sempre atualizado")
    print("   ✅ Horários de início e fim claros")
    print("   ✅ Campo message com informações descritivas")
    print("   ✅ Volume de dados (lidos e gravados)")
    print("   ✅ Arquivos ingeridos com nomes")
    print("   ✅ Tamanho dos arquivos em bytes")
    print("\n✅ Demonstração concluída!")
