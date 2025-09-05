"""
🦕 DINO SDK - Exemplo de Uso do IngestionEngine

Este exemplo demonstra como usar o IngestionEngine para ingestão de dados CSV
usando AutoLoader e salvando no Unity Catalog.

IMPORTANTE: Este exemplo assume que 'spark' está disponível globalmente,
como é o caso em notebooks Databricks. Para usar em outros ambientes,
descomente as linhas de criação do SparkSession.
"""

from pyspark.sql import SparkSession
from src.dino_sdk.ingestion_engine import (
    IngestionEngine, 
    IngestionConfig, 
    ingest_csv_to_unity_catalog
)

# Para ambientes que não têm spark global (descomente se necessário):
# spark = SparkSession.builder.appName("DINO SDK Ingestion").getOrCreate()

def exemplo_basico():
    """
    Exemplo básico de ingestão usando função de conveniência.
    """
    print("🦕 DINO SDK - Exemplo Básico de Ingestão")
    print("=" * 50)
    
    # ⚠️ IMPORTANTE: Assumindo que 'spark' está disponível globalmente (Databricks)
    # Para outros ambientes, descomente e configure:
    # spark = SparkSession.builder.appName("DINO SDK Ingestion").getOrCreate()
    
    # Parâmetros de exemplo
    source_path = "/mnt/data/csv_files/"
    catalog_name = "data_master_dev_dbw"  
    schema_name = "raw_data"
    table_name = "customer_data"
    
    try:
        # Ingestão usando função de conveniência (batch)
        print("📥 Iniciando ingestão batch...")
        
        # NOTA: 'spark' deve estar disponível no contexto global
        result = ingest_csv_to_unity_catalog(
            spark=spark,  # Assumindo contexto Databricks
            source_path=source_path,
            catalog_name=catalog_name,
            schema_name=schema_name,
            table_name=table_name,
            file_header=True,
            file_delimiter=",",
            type_run="batch"
        )
        
        print("✅ Ingestão batch concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_avancado():
    """
    Exemplo avançado usando IngestionEngine diretamente.
    """
    print("\n🦕 DINO SDK - Exemplo Avançado de Ingestão")
    print("=" * 50)
    
    # ⚠️ IMPORTANTE: 'spark' deve estar disponível
    # Criar engine
    engine = IngestionEngine(spark)  # Assumindo contexto Databricks
    
    # Configuração personalizada
    config = IngestionConfig(
        # Origem
        source_path="/mnt/data/complex_csv/",
        file_extension="csv",
        file_header=True,
        file_delimiter="|",  # Delimitador personalizado
        multiline=True,      # Suporte a multiline
        
        # Destino Unity Catalog
        catalog_name="data_master_dev_dbw",
        schema_name="processed_data",
        table_name="complex_customer_data",
        
        # Execução
        type_run="streaming",
        trigger_processing_time="30 seconds",
        
        # AutoLoader avançado
        schema_evolution_mode="addNewColumns",
        rescue_data_column="_rescued_data",
        
        # Configurações Spark personalizadas
        custom_spark_config={
            "cloudFiles.maxFilesPerTrigger": "100",
            "cloudFiles.maxBytesPerTrigger": "1g"
        }
    )
    
    try:
        print("📡 Iniciando ingestão streaming...")
        
        # Executar ingestão
        streaming_query = engine.ingest(config)
        
        if streaming_query:
            print(f"✅ Stream iniciado: {streaming_query.id}")
            print("💡 Para parar: streaming_query.stop()")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_validacao_schema():
    """
    Exemplo mostrando validação e criação de schema.
    """
    print("\n🦕 DINO SDK - Validação de Schema")
    print("=" * 50)
    
    from src.dino_sdk.schema_manager import SchemaManager
    
    # Verificar/criar schema antes da ingestão
    schema_manager = SchemaManager("data_master_dev_dbw", "raw_data")
    
    try:
        # Verificar se schema existe
        if not schema_manager.schema_exists(spark):
            print("📂 Schema não existe, criando...")
            result = schema_manager.create_schema(spark)
            if result['success']:
                print("✅ Schema criado com sucesso!")
            else:
                print(f"❌ Erro ao criar schema: {result['errors']}")
                return
        else:
            print("✅ Schema já existe")
        
        # Agora fazer a ingestão
        print("📥 Iniciando ingestão...")
        result = ingest_csv_to_unity_catalog(
            spark=spark,
            source_path="/mnt/data/sales/",
            catalog_name="data_master_dev_dbw",
            schema_name="raw_data", 
            table_name="sales_data",
            type_run="batch"
        )
        
        print("✅ Pipeline completo concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_monitoramento():
    """
    Exemplo de monitoramento de ingestão streaming.
    """
    print("\n🦕 DINO SDK - Monitoramento de Streaming")
    print("=" * 50)
    
    engine = IngestionEngine(spark)
    
    config = IngestionConfig(
        source_path="/mnt/data/streaming_csv/",
        catalog_name="data_master_dev_dbw",
        schema_name="streaming_data",
        table_name="realtime_events",
        type_run="streaming",
        trigger_processing_time="5 seconds"
    )
    
    try:
        # Iniciar streaming
        query = engine.ingest(config)
        
        if query:
            print(f"📡 Stream ID: {query.id}")
            print(f"🎯 Tabela destino: {config.catalog_name}.{config.schema_name}.{config.table_name}")
            
            # Monitorar por alguns segundos (exemplo)
            import time
            for i in range(5):
                if query.isActive:
                    progress = query.lastProgress
                    if progress:
                        print(f"📊 Batch {i+1}: {progress.get('inputRowsPerSecond', 0)} rows/sec")
                    time.sleep(10)
                else:
                    print("⚠️ Query não está ativa")
                    break
            
            # Parar stream (opcional)
            # query.stop()
            # print("🛑 Stream parado")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    # Executar exemplos
    exemplo_basico()
    exemplo_avancado() 
    exemplo_validacao_schema()
    exemplo_monitoramento()
    
    print("\n🎉 Todos os exemplos executados!")
    print("💡 Adapte os caminhos e nomes para seu ambiente específico")
