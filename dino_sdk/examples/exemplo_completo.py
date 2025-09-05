#!/usr/bin/env python3
"""
🦕 DINO SDK v1.2.0 - Exemplo Completo de Uso

Este exemplo demonstra como usar o DINO SDK para:
1. Criar schemas com volumes gerenciados
2. Ingerir dados com AutoLoader e Liquid Clustering
3. Validar resultados

Desenvolvido para Databricks Unity Catalog
"""

# === IMPORTS ===
from dino_sdk import IngestionEngine, IngestionConfig
from dino_sdk.schema_manager import ensure_schema_simple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(spark):
    """
    Função principal demonstrando uso completo do DINO SDK
    
    Args:
        spark: SparkSession do Databricks
    """
    
    print("🦕 DINO SDK v1.2.0 - Exemplo Completo")
    print("=" * 50)
    
    # === CONFIGURAÇÃO ===
    catalog_name = "main"
    schema_name = "bronze_example"
    table_name = "sales_data"
    source_path = "/Volumes/main/default/raw/sales/"  # Ajuste conforme necessário
    
    try:
        # === PASSO 1: CRIAR SCHEMA COM VOLUMES ===
        print("\n🏗️ Passo 1: Criando schema com volumes...")
        
        result = ensure_schema_simple(spark, catalog_name, schema_name)
        
        if result['success']:
            print("✅ Schema criado com sucesso!")
            if result.get('volumes_created'):
                print(f"📦 Volumes criados: {result['volumes_created']}")
            if result.get('volumes_existing'):
                print(f"📦 Volumes existentes: {result['volumes_existing']}")
        else:
            print("❌ Erro na criação do schema:")
            for error in result['errors']:
                print(f"   • {error}")
            return False
        
        # === PASSO 2: CONFIGURAR INGESTÃO ===
        print("\n⚙️ Passo 2: Configurando ingestão...")
        
        config = IngestionConfig(
            # Dados de origem
            source_path=source_path,
            file_extension="csv",
            
            # Destino Unity Catalog
            catalog_name=catalog_name,
            schema_name=schema_name,
            table_name=table_name,
            
            # Funcionalidades avançadas
            liquid_clustering=True,
            clustering_columns=["region", "category"],
            schema_evolution_mode="rescue",
            rescue_data_column="_rescued_data",
            
            # Processamento
            type_run="batch",  # ou "streaming" para dados contínuos
            
            # Metadados
            table_comment="Tabela criada pelo DINO SDK - Exemplo Completo",
            add_ingestion_metadata=True
        )
        
        print("✅ Configuração criada:")
        print(f"   • Origem: {config.source_path}")
        print(f"   • Destino: {config.catalog_name}.{config.schema_name}.{config.table_name}")
        print(f"   • Clustering: {config.clustering_columns}")
        
        # === PASSO 3: EXECUTAR INGESTÃO ===
        print("\n🚀 Passo 3: Executando ingestão...")
        
        engine = IngestionEngine(config, spark)
        result = engine.process_data()
        
        if result['success']:
            print("✅ Ingestão concluída com sucesso!")
            
            # Exibir métricas se disponíveis
            if 'records_processed' in result:
                print(f"📊 Registros processados: {result['records_processed']}")
            if 'execution_time' in result:
                print(f"⏱️ Tempo de execução: {result['execution_time']:.2f}s")
                
        else:
            print("❌ Erro na ingestão:")
            for error in result.get('errors', []):
                print(f"   • {error}")
            return False
        
        # === PASSO 4: VALIDAR RESULTADOS ===
        print("\n✅ Passo 4: Validando resultados...")
        
        table_full_name = f"{catalog_name}.{schema_name}.{table_name}"
        
        try:
            # Verificar dados
            df = spark.table(table_full_name)
            record_count = df.count()
            
            print(f"✅ Tabela criada: {table_full_name}")
            print(f"📊 Total de registros: {record_count}")
            
            # Mostrar schema
            print("\n📋 Schema da tabela:")
            df.printSchema()
            
            # Mostrar amostra dos dados
            print("\n📋 Primeiros 5 registros:")
            df.show(5)
            
            # Verificar clustering se aplicável
            if hasattr(df, 'columns') and 'region' in df.columns:
                print("\n🌍 Distribuição por região:")
                df.groupBy("region").count().orderBy("count", ascending=False).show()
                
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False
        
        print("\n🎉 Exemplo executado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        print(f"❌ Erro geral: {e}")
        return False


def exemplo_streaming(spark):
    """
    Exemplo específico para processamento streaming
    
    Args:
        spark: SparkSession do Databricks
    """
    
    print("\n🌊 Exemplo de Streaming com DINO SDK")
    print("=" * 40)
    
    # Configuração para streaming
    config = IngestionConfig(
        source_path="/mnt/streaming-data/sales/",
        catalog_name="main",
        schema_name="bronze_streaming",
        table_name="sales_realtime",
        file_extension="json",
        
        # Streaming específico
        type_run="streaming",
        schema_evolution_mode="addNewColumns",
        
        # AutoLoader otimizado para streaming
        max_files_per_trigger=100,
        
        # Clustering para performance
        liquid_clustering=True,
        clustering_columns=["event_date", "region"]
    )
    
    print("⚙️ Configuração streaming criada")
    print(f"   • Trigger: máximo {config.max_files_per_trigger} arquivos por batch")
    print(f"   • Schema evolution: {config.schema_evolution_mode}")
    
    # Nota: Em streaming, geralmente você executaria em um job contínuo
    print("💡 Para streaming, execute em um Databricks Job para processamento contínuo")


def exemplo_cli():
    """
    Demonstração dos comandos CLI do DINO SDK
    """
    
    print("\n💻 Comandos CLI do DINO SDK")
    print("=" * 35)
    
    cli_examples = [
        "# Ver configurações atuais",
        "dino-config show",
        "",
        "# Gerar código para criar schema",
        "dino-config create-schema --catalog-name main --schema-name bronze",
        "",
        "# Com localização personalizada",
        "dino-config create-schema --catalog-name vendas --schema-name silver \\",
        "  --managed-location 'abfss://container@storage.dfs.core.windows.net/vendas/silver/'",
        "",
        "# Ver ajuda completa",
        "dino-config --help"
    ]
    
    for line in cli_examples:
        if line.startswith("#"):
            print(f"\n💡 {line}")
        else:
            print(f"   {line}")


if __name__ == "__main__":
    """
    Execução standalone (apenas para referência)
    No Databricks, use as funções diretamente passando spark como parâmetro
    """
    
    print("🦕 DINO SDK - Exemplo de Uso")
    print("Este script deve ser executado em um notebook Databricks")
    print("\nPara usar:")
    print("1. Importe este módulo em seu notebook")
    print("2. Chame main(spark) com sua SparkSession")
    print("3. Ajuste os caminhos conforme necessário")
    
    # Exemplo de uso em notebook:
    example_usage = """
    # Exemplo de uso em notebook Databricks:
    
    from examples.exemplo_completo import main, exemplo_streaming
    
    # Executar exemplo principal
    success = main(spark)
    
    if success:
        print("✅ Exemplo executado com sucesso!")
    else:
        print("❌ Verifique os logs para detalhes do erro")
    
    # Executar exemplo de streaming
    exemplo_streaming(spark)
    """
    
    print(example_usage)


# === CONFIGURAÇÕES ADICIONAIS ===

def configurar_secrets_azure(spark):
    """
    Exemplo de configuração de secrets para Azure Data Lake
    
    Args:
        spark: SparkSession
    """
    
    print("\n🔐 Configurando acesso ao Azure Data Lake...")
    
    # Usando Service Principal (recomendado para produção)
    try:
        tenant_id = "your-tenant-id"
        
        # Configurar autenticação OAuth
        spark.conf.set(
            "fs.azure.account.auth.type.yourstorageaccount.dfs.core.windows.net", 
            "OAuth"
        )
        spark.conf.set(
            "fs.azure.account.oauth.provider.type.yourstorageaccount.dfs.core.windows.net",
            "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
        )
        spark.conf.set(
            "fs.azure.account.oauth2.client.id.yourstorageaccount.dfs.core.windows.net",
            dbutils.secrets.get(scope="azure-scope", key="client-id")
        )
        spark.conf.set(
            "fs.azure.account.oauth2.client.secret.yourstorageaccount.dfs.core.windows.net",
            dbutils.secrets.get(scope="azure-scope", key="client-secret")
        )
        spark.conf.set(
            "fs.azure.account.oauth2.client.endpoint.yourstorageaccount.dfs.core.windows.net",
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
        )
        
        print("✅ Configuração Azure concluída")
        
    except Exception as e:
        print(f"⚠️ Configure os secrets antes: {e}")


def otimizacoes_performance(spark):
    """
    Configurações recomendadas para melhor performance
    
    Args:
        spark: SparkSession
    """
    
    print("\n⚡ Configurações de Performance...")
    
    # Configurações recomendadas
    performance_configs = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true", 
        "spark.databricks.delta.autoCompact.enabled": "true",
        "spark.databricks.delta.optimizeWrite.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true"
    }
    
    for config, value in performance_configs.items():
        spark.conf.set(config, value)
        print(f"✅ {config} = {value}")
    
    print("⚡ Configurações de performance aplicadas!")


"""
🦕 DINO SDK v1.2.0 - Exemplo Completo

FUNCIONALIDADES DEMONSTRADAS:
✅ Criação de schemas com volumes gerenciados
✅ Ingestão com AutoLoader e Liquid Clustering  
✅ Processamento batch e streaming
✅ Validação e verificação de resultados
✅ Configurações de secrets e performance
✅ Exemplos de CLI

COMO USAR:
1. Execute em notebook Databricks
2. Ajuste caminhos e configurações
3. Chame main(spark) para executar exemplo completo
4. Use exemplo_streaming(spark) para casos de streaming

DINO SDK - Simplifique sua ingestão no Databricks! 🚀
"""
