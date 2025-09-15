#!/usr/bin/env python3
"""
Dino SDK - CLI Configuration Tool (Simplified)
Ferramenta de configuração via linha de comando do Dino SDK - Versão Simplificada
"""

import click
import os
from pyspark.sql import SparkSession
from .config_manager import get_config_manager
from .dino_sdk.schema_manager import SchemaManager, create_schema_simple


@click.group()
def config():
    """🦕 Dino SDK - Ferramenta de configuração"""
    pass


@config.command()
def show():
    """
    Mostrar configuração atual do DINO SDK

    Exemplo:
        dino-config show
    """
    print("🦕 Dino SDK - Configuração Atual")
    print("=" * 50)
    
    config_manager = get_config_manager()
    config_dict = config_manager.get_all_variables()
    
    # Mostrar configurações organizadamente
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


@config.command()
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
@click.option('--schema-name', required=True, help='Nome do schema a ser criado')
@click.option('--managed-location', help='Localização gerenciada opcional')
def create_schema(catalog_name: str, schema_name: str, managed_location: str = None):
    """
    Mostrar como criar schema no Unity Catalog
    
    NOTA: Este comando apenas mostra o código Python a ser executado em um notebook Databricks.
    A execução real requer uma sessão Spark ativa.
    
    Exemplos:
        dino-config create-schema --catalog-name main --schema-name bronze
        dino-config create-schema --catalog-name vendas --schema-name silver --managed-location abfss://container@storage.dfs.core.windows.net/vendas/silver/
    """
    print("🏗️ Dino SDK - Como Criar Schema")
    print("=" * 40)
    print()
    print("📋 Para criar o schema especificado, execute o seguinte código em um notebook Databricks:")
    print()
    
    # Mostrar código Python para execução
    print("```python")
    print("# Importar as classes necessárias")
    print("from pyspark.sql import SparkSession")
    print("from src.dino_sdk.schema_manager import SchemaManager, create_schema_simple")
    print()
    print("# spark já está disponível globalmente no Databricks")
    print()
    print("# Método 1: Usando a classe SchemaManager")
    print(f'manager = SchemaManager("{catalog_name}", "{schema_name}")')
    
    if managed_location:
        print(f'result = manager.create_schema(spark, managed_location="{managed_location}")')
    else:
        print('result = manager.create_schema(spark)')
    
    print()
    print("# Método 2: Usando função de conveniência")
    if managed_location:
        print(f'result = create_schema_simple(spark, "{catalog_name}", "{schema_name}", "{managed_location}")')
    else:
        print(f'result = create_schema_simple(spark, "{catalog_name}", "{schema_name}")')
    
    print()
    print("# Verificar resultado")
    print("if result['success']:")
    print("    print('✅ Schema criado com sucesso!')")
    print("    # Obter informações do schema")
    print(f"    info = manager.get_schema_info(spark)")
    print("    print(f'Tabelas no schema: {len(info[\"tables\"])}')")
    print("else:")
    print("    print('❌ Erro na criação:')")
    print("    for error in result['errors']:")
    print("        print(f'  • {error}')")
    print("```")
    print()
    print("📊 Parâmetros especificados:")
    print(f"   • Catálogo: {catalog_name}")
    print(f"   • Schema: {schema_name}")
    if managed_location:
        print(f"   • Localização: {managed_location}")
    else:
        print(f"   • Localização: Será obtida automaticamente do catálogo")
    print()
    print("💡 Dica: Cole e execute esse código em uma célula do seu notebook Databricks!")


@config.command()
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
@click.option('--schema-name', required=True, help='Nome do schema')
def validate_schema(catalog_name: str, schema_name: str):
    """
    Mostrar como validar schema no Unity Catalog
    
    NOTA: Este comando apenas mostra o código Python a ser executado em um notebook Databricks.
    
    Exemplos:
        dino-config validate-schema --catalog-name main --schema-name bronze
    """
    print("🔍 Dino SDK - Como Validar Schema")
    print("=" * 35)
    print()
    print("📋 Para validar o schema, execute o seguinte código em um notebook Databricks:")
    print()
    
    print("```python")
    print("# Importar as classes necessárias")  
    print("from src.dino_sdk.schema_manager import SchemaManager")
    print()
    print("# spark já está disponível globalmente no Databricks")
    print()
    print(f'manager = SchemaManager("{catalog_name}", "{schema_name}")')
    print()
    print("# Verificar se catálogo existe")
    print("if manager.catalog_exists(spark):")
    print("    print('✅ Catálogo existe')")
    print("    ")
    print("    # Verificar se schema existe")
    print("    if manager.schema_exists(spark):")
    print("        print('✅ Schema existe')")
    print("        ")
    print("        # Obter informações detalhadas")
    print("        info = manager.get_schema_info(spark)")
    print("        print(f'📊 Informações do schema:')")
    print("        print(f'   • Catálogo existe: {info[\"catalog_exists\"]}')")
    print("        print(f'   • Schema existe: {info[\"schema_exists\"]}')")
    print("        print(f'   • Número de tabelas: {len(info[\"tables\"])}')")
    print("        print(f'   • External location: {info[\"external_location\"]}')")
    print("        ")
    print("        if info['tables']:")
    print("            print('📋 Tabelas no schema:')")
    print("            for table in info['tables']:")
    print("                print(f'   • {table}')")
    print("    else:")
    print("        print('❌ Schema não existe')")
    print("else:")
    print("    print('❌ Catálogo não existe')")
    print("```")
    print()
    print("📊 Parâmetros especificados:")
    print(f"   • Catálogo: {catalog_name}")
    print(f"   • Schema: {schema_name}")
    print()
    print("💡 Dica: Cole e execute esse código em uma célula do seu notebook Databricks!")


@config.command()
def examples():
    """
    Mostrar exemplos de uso do SchemaManager
    """
    print("🦕 Dino SDK - Exemplos de Uso")
    print("=" * 35)
    print()
    print("📚 Exemplos práticos para usar em notebooks Databricks:")
    print()
    
    print("🏗️ 1. CRIAR SCHEMA BÁSICO")
    print("-" * 25)
    print("```python")
    print("from src.dino_sdk.schema_manager import create_schema_simple")
    print()
    print("result = create_schema_simple(spark, 'main', 'bronze_vendas')")
    print("print('✅ Schema criado!' if result['success'] else '❌ Erro na criação')")
    print("```")
    print()
    
    print("📊 2. VALIDAR E OBTER INFORMAÇÕES")
    print("-" * 35)
    print("```python")
    print("from src.dino_sdk.schema_manager import SchemaManager")
    print()
    print("manager = SchemaManager('main', 'bronze_vendas')")
    print("info = manager.get_schema_info(spark)")
    print()
    print("print(f'Catálogo existe: {info[\"catalog_exists\"]}')")
    print("print(f'Schema existe: {info[\"schema_exists\"]}')")
    print("print(f'Tabelas: {len(info[\"tables\"])}')")
    print("```")
    print()
    
    print("🔄 3. PIPELINE BRONZE/SILVER/GOLD")
    print("-" * 35)
    print("```python")
    print("from src.dino_sdk.schema_manager import create_schema_simple")
    print()
    print("# Criar todos os schemas do pipeline")
    print("schemas = ['bronze', 'silver', 'gold']")
    print("for schema in schemas:")
    print("    result = create_schema_simple(spark, 'main', schema)")
    print("    print(f'Schema {schema}: {'✅' if result['success'] else '❌'}')")
    print("```")
    print()
    
    print("📁 4. SCHEMA COM LOCALIZAÇÃO ESPECÍFICA")
    print("-" * 40)
    print("```python")
    print("from src.dino_sdk.schema_manager import SchemaManager")
    print()
    print("manager = SchemaManager('vendas', 'silver')")
    print("location = 'abfss://vendas@storage.dfs.core.windows.net/silver/'")
    print("result = manager.create_schema(spark, managed_location=location)")
    print("```")
    print()
    
    print("💡 Dica: Todos os exemplos assumem que 'spark' está disponível no notebook!")


if __name__ == "__main__":
    config()
