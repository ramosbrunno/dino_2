#!/usr/bin/env python3
"""
🦕 DINO SDK v2.5.0 - Exemplo de Sistema de Logging Abrangente

Este exemplo demonstra as novas funcionalidades de logging do DINO SDK v2.5.0:
- Status da execução: iniciado, concluído com sucesso ou com erro  
- Volume de dados: quantidade de registros lidos e gravados
- Paths utilizados: caminhos de origem e destino dos arquivos
- Tempo total de execução
- Detalhamento de erros com stack trace
"""

from pyspark.sql import SparkSession
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig

def main():
    """Exemplo de uso do sistema de logging abrangente"""
    
    # 1. Criar sessão Spark
    spark = SparkSession.builder \
        .appName("DINO SDK Logging Example") \
        .config("spark.sql.catalog.main", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
    
    # 2. Criar engine de ingestão
    engine = IngestionEngine(spark)
    
    # 3. Configurar ingestão
    config = IngestionConfig(
        source_path="/Volumes/main/demo/raw/vendas_2024.csv",
        catalog_name="main",
        schema_name="demo", 
        table_name="vendas_logs_exemplo",
        type_run="batch",
        file_extension="csv",
        file_header=True,
        file_delimiter=","
    )
    
    print("🚀 Iniciando exemplo de sistema de logging DINO SDK v2.5.0")
    print("=" * 60)
    
    # 4. Executar ingestão com logging automático
    resultado = engine.ingest(config)
    
    print("\n📊 RESULTADO DA INGESTÃO:")
    print("=" * 60)
    
    if resultado["success"]:
        print(f"✅ Status: Sucesso")
        print(f"🔍 Execution ID: {resultado['execution_id']}")
        print(f"📊 Registros lidos: {resultado.get('records_read', 'N/A')}")
        print(f"📊 Registros gravados: {resultado.get('records_written', 'N/A')}")
        print(f"⏱️ Tempo de execução: {resultado.get('execution_duration_seconds', 'N/A')}s")
        print(f"📁 Source: {resultado.get('source_path', 'N/A')}")
        print(f"📁 Destination: {resultado.get('destination_path', 'N/A')}")
        print(f"💾 Tabela: {resultado.get('table', 'N/A')}")
    else:
        print(f"❌ Status: Erro")
        print(f"🔍 Execution ID: {resultado.get('execution_id', 'N/A')}")
        print(f"❌ Erro: {resultado.get('error', 'N/A')}")
        print(f"📊 Registros lidos: {resultado.get('records_read', 'N/A')}")
        print(f"📊 Registros gravados: {resultado.get('records_written', 'N/A')}")
        
        # Stack trace se disponível
        if resultado.get('error_stack_trace'):
            print(f"\n🔍 Stack Trace:")
            print("=" * 40)
            print(resultado['error_stack_trace'])
    
    # 5. Consultar histórico de execuções
    print("\n📈 HISTÓRICO DE EXECUÇÕES:")
    print("=" * 60)
    
    try:
        historico = engine.get_ingestion_history(
            catalog_name="main",
            schema_name="demo",
            table_name="vendas_logs_exemplo",
            limit=5
        )
        
        print("🔍 Últimas 5 execuções:")
        historico.show(truncate=False)
        
    except Exception as e:
        print(f"⚠️ Erro ao consultar histórico: {e}")
    
    # 6. Exemplo de consulta de histórico geral (todas as tabelas)
    print("\n📈 HISTÓRICO GERAL DO SCHEMA:")
    print("=" * 60)
    
    try:
        historico_geral = engine.get_ingestion_history(
            catalog_name="main",
            schema_name="demo",
            table_name=None,  # Todas as tabelas
            limit=10
        )
        
        print("🔍 Últimas 10 execuções no schema:")
        historico_geral.show(10, truncate=False)
        
    except Exception as e:
        print(f"⚠️ Erro ao consultar histórico geral: {e}")
    
    # 7. Finalizar
    spark.stop()
    print("\n✅ Exemplo concluído!")
    print("=" * 60)
    print("💡 Verifique a tabela main.demo.dino_ingestion_logs para ver todos os logs")

if __name__ == "__main__":
    main()
