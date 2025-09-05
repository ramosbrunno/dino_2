# exemplo_novo_padrao.py
"""
DINO SDK v1.2.0 - Exemplo do Novo Padrão
Demonstra como usar o padrão simplificado com spark como parâmetro
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_date
from src.config_operations import ConfigOperations
from src.config_manager import get_config_manager


def exemplo_leitura_dados(spark: SparkSession, caminho: str) -> DataFrame:
    """
    Exemplo de função seguindo o novo padrão - recebe spark como parâmetro
    
    Args:
        spark: Sessão Spark ativa
        caminho: Caminho para os dados
        
    Returns:
        DataFrame com os dados lidos
    """
    try:
        # Usar spark diretamente - sem SparkSessionManager
        df = (spark.read
              .option("header", "true")
              .option("inferSchema", "true")
              .csv(caminho)
              .select(
                  "*",
                  current_date().alias("data_processamento"),
                  col("_metadata").alias("metadados") if "_metadata" in spark.read.csv(caminho).columns else None
              ))
        
        print(f"✅ Dados lidos com sucesso: {df.count()} registros")
        return df
        
    except Exception as e:
        print(f"❌ Erro na leitura: {e}")
        return None


def exemplo_configuracao_unity_catalog(spark: SparkSession):
    """
    Exemplo de configuração do Unity Catalog seguindo o novo padrão
    
    Args:
        spark: Sessão Spark ativa
    """
    try:
        # Usar ConfigOperations com spark como parâmetro
        result = ConfigOperations.validate_catalog_schema(
            spark=spark,
            catalog_name="main", 
            schema_name="bronze"
        )
        
        if result['success']:
            print("✅ Unity Catalog validado com sucesso!")
            
            # Setup de novo projeto
            setup_result = ConfigOperations.setup_unity_catalog(
                spark=spark,
                project_name="exemplo_projeto",
                storage_name="storage_exemplo", 
                catalog_name="main",
                schema_name="bronze"
            )
            
            if setup_result['success']:
                print("✅ Projeto configurado no Unity Catalog!")
            else:
                print(f"❌ Erro no setup: {setup_result['errors']}")
        else:
            print(f"❌ Erro na validação: {result['errors']}")
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")


def exemplo_processamento_completo(spark: SparkSession):
    """
    Exemplo completo de processamento seguindo o novo padrão
    
    Args:
        spark: Sessão Spark ativa
    """
    try:
        # 1. Obter configurações
        config_manager = get_config_manager()
        catalog_name = config_manager.get('catalog_name', 'main')
        schema_name = config_manager.get('schema_name', 'bronze')
        
        print(f"📊 Usando catálogo: {catalog_name}.{schema_name}")
        
        # 2. Validar ambiente
        validation = ConfigOperations.validate_catalog_schema(
            spark, catalog_name, schema_name
        )
        
        if not validation['success']:
            print("⚠️ Validação falhou, mas continuando com processamento...")
        
        # 3. Criar tabela de exemplo
        df_exemplo = spark.range(1000).select(
            col("id"),
            (col("id") * 2).alias("valor"),
            current_date().alias("data_criacao")
        )
        
        # 4. Salvar no Unity Catalog
        tabela_destino = f"{catalog_name}.{schema_name}.exemplo_dino_sdk"
        
        (df_exemplo.write
         .mode("overwrite")
         .option("overwriteSchema", "true")
         .saveAsTable(tabela_destino))
        
        print(f"✅ Tabela criada: {tabela_destino}")
        
        # 5. Verificar dados
        contagem = spark.table(tabela_destino).count()
        print(f"📊 Registros na tabela: {contagem}")
        
        return df_exemplo
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return None


# Exemplo de uso em notebook Databricks:
"""
# No notebook Databricks, usar assim:

# 1. spark já está disponível globalmente
exemplo_leitura_dados(spark, "/mnt/dados/arquivo.csv")

# 2. Configurar Unity Catalog  
exemplo_configuracao_unity_catalog(spark)

# 3. Processamento completo
df_resultado = exemplo_processamento_completo(spark)

# 4. CLI continua funcionando independentemente
%sh dino-config show
%sh dino-config validate --catalog-name main --schema-name bronze
%sh dino-config setup --project-name novo_projeto --storage-name storage123 --catalog-name main --schema-name bronze
"""

if __name__ == "__main__":
    print("🦕 DINO SDK v1.2.0 - Exemplo do Novo Padrão")
    print("=" * 50)
    print()
    print("Este arquivo demonstra o novo padrão de usar spark como parâmetro.")
    print("Para usar em produção:")
    print("1. Execute em um notebook Databricks onde 'spark' está disponível")
    print("2. Passe 'spark' como primeiro parâmetro para todas as funções")
    print("3. Use ConfigOperations para operações de Unity Catalog")
    print("4. Use CLI para configurações gerais")
    print()
    print("✅ Padrão mais limpo, simples e confiável!")
