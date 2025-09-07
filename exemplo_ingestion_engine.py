#!/usr/bin/env python3
"""
🦕 DINO SDK - Exemplo Prático do IngestionEngine

Este script demonstra como usar o IngestionEngine do DINO SDK para ingestão de dados.
"""

from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig
import logging

def exemplo_basico():
    """Exemplo básico de uso do IngestionEngine"""
    
    print("🦕 DINO SDK - Exemplo Básico do IngestionEngine")
    print("=" * 50)
    
    # 1. Configuração básica
    config = IngestionConfig(
        source_path="/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/vendas_2024/",
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes", 
        table_name="vendas_exemplo",
        file_extension="parquet"
    )
    
    print("📋 Configuração criada:")
    print(f"   Source: {config.source_path}")
    print(f"   Destino: {config.catalog_name}.{config.schema_name}.{config.table_name}")
    print(f"   Formato: {config.file_extension}")
    
    try:
        # 2. Inicializar engine
        print("\n🔧 Inicializando IngestionEngine...")
        engine = IngestionEngine()
        print("✅ Engine inicializado")
        
        # 3. Executar ingestão
        print("\n🚀 Iniciando ingestão...")
        result = engine.ingest(config)
        
        # 4. Verificar resultado
        if result["success"]:
            print("✅ Ingestão concluída com sucesso!")
            print(f"📊 Modo: {result['mode']}")
            print(f"📂 Tabela: {result['table']}")
            print(f"💬 Mensagem: {result['message']}")
        else:
            print("❌ Falha na ingestão")
            print(f"Erro: {result.get('error', 'Erro desconhecido')}")
            
        return result
        
    except Exception as e:
        print(f"💥 Exceção: {str(e)}")
        return {"success": False, "error": str(e)}

def exemplo_avancado():
    """Exemplo avançado com todas as configurações"""
    
    print("\n🦕 DINO SDK - Exemplo Avançado do IngestionEngine")
    print("=" * 50)
    
    # Configuração completa
    config = IngestionConfig(
        # Origem
        source_path="/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/vendas_detalhadas/",
        file_extension="csv",
        file_header=True,
        file_delimiter=",",
        
        # Destino
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes",
        table_name="vendas_detalhadas_exemplo",
        
        # Execução
        type_run="batch",
        
        # AutoLoader
        schema_evolution_mode="rescue",
        multiline=False,
        rescue_data_column="_rescued",
        
        # Metadados
        add_metadata=True,
        metadata_columns=["_file_path", "_file_modification_time"]
    )
    
    print("📋 Configuração avançada:")
    for attr, value in config.__dict__.items():
        print(f"   {attr}: {value}")
    
    try:
        engine = IngestionEngine()
        result = engine.ingest(config)
        
        print(f"\n📊 Resultado: {result}")
        return result
        
    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        return {"success": False, "error": str(e)}

def exemplo_streaming():
    """Exemplo de ingestão streaming"""
    
    print("\n🦕 DINO SDK - Exemplo Streaming do IngestionEngine")
    print("=" * 50)
    
    config = IngestionConfig(
        source_path="/Volumes/data_master_dev_dbw/bronze_test_volumes/streaming/",
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes",
        table_name="eventos_streaming",
        file_extension="json",
        type_run="streaming",
        trigger_processing_time="10 seconds"
    )
    
    print("🔄 Configuração para streaming:")
    print(f"   Trigger: {config.trigger_processing_time}")
    print(f"   Tipo: {config.type_run}")
    
    try:
        engine = IngestionEngine()
        result = engine.ingest(config)
        
        if result["success"] and result["mode"] == "streaming":
            print("✅ Stream iniciado com sucesso!")
            print(f"🆔 Stream ID: {result.get('stream_id', 'N/A')}")
            print("💡 Para parar o stream, use spark.streams.active[0].stop()")
        
        return result
        
    except Exception as e:
        print(f"💥 Erro no streaming: {str(e)}")
        return {"success": False, "error": str(e)}

def validar_resultado(catalog, schema, table):
    """Valida se a ingestão foi bem-sucedida"""
    
    print(f"\n🔍 Validando resultado da ingestão...")
    
    try:
        # Simular consulta (em um notebook seria: spark.sql)
        table_full = f"{catalog}.{schema}.{table}"
        print(f"📂 Verificando tabela: {table_full}")
        
        # Em um ambiente real, você faria:
        # count = spark.sql(f"SELECT COUNT(*) as total FROM {table_full}").collect()[0]['total']
        # print(f"📊 Total de registros: {count}")
        
        # Para este exemplo, apenas simular
        print("✅ Validação simulada - em um notebook Databricks, use:")
        print(f"   count = spark.sql('SELECT COUNT(*) FROM {table_full}').collect()[0][0]")
        print(f"   display(spark.sql('SELECT * FROM {table_full} LIMIT 10'))")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False

def main():
    """Função principal - executa todos os exemplos"""
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    print("🦕 DINO SDK - Exemplos do IngestionEngine")
    print("=" * 60)
    print("📝 Este script demonstra como usar o IngestionEngine")
    print("💡 Execute em um notebook Databricks para funcionalidade completa")
    print()
    
    # Exemplo 1: Básico
    try:
        result1 = exemplo_basico()
        if result1.get("success"):
            validar_resultado("data_master_dev_dbw", "bronze_test_volumes", "vendas_exemplo")
    except Exception as e:
        print(f"❌ Erro no exemplo básico: {e}")
    
    # Exemplo 2: Avançado
    try:
        result2 = exemplo_avancado()
        if result2.get("success"):
            validar_resultado("data_master_dev_dbw", "bronze_test_volumes", "vendas_detalhadas_exemplo")
    except Exception as e:
        print(f"❌ Erro no exemplo avançado: {e}")
    
    # Exemplo 3: Streaming (comentado por ser contínuo)
    print("\n💡 Exemplo de streaming disponível na função exemplo_streaming()")
    print("   Para testar streaming, execute: exemplo_streaming()")
    
    print("\n🎉 Exemplos concluídos!")
    print("📚 Para mais informações, consulte: GUIA_INGESTION_ENGINE.md")

if __name__ == "__main__":
    main()
