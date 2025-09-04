#!/usr/bin/env python3
"""
Dino SDK - Comando de Configuração
Configuração inicial e gerenciamento de variáveis de ambiente
"""

import click
import os
import json
from pathlib import Path
from typing import Dict, Any

from .config_manager import get_config_manager
from .spark_session_manager import SparkSessionManager


@click.group()
def config():
    """Comandos de configuração do Dino SDK"""
    pass


@config.command()
@click.option('--project-name', required=True, help='Nome do projeto')
@click.option('--storage-name', required=True, help='Nome do storage account')
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
@click.option('--schema-name', required=True, help='Nome do schema a ser criado')
def setup(project_name: str, storage_name: str, catalog_name: str, schema_name: str):
    """
    Configurar DINO SDK com Unity Catalog

    Exemplos:
        dino-config setup --project-name vendas --storage-name storagevendas --catalog-name main --schema-name bronze
        dino-config setup --project-name marketing --storage-name stgmarketing --catalog-name analytics --schema-name silver
    """
    print("🦕 Dino SDK - Configuração Simplificada")
    print("=" * 45)
    
    try:
        # Usar SparkSessionManager para detecção robusta
        print("🔍 Detectando ambiente Spark...")
        spark_session = SparkSessionManager.get_spark_session("DINO Config Setup")
        
        if spark_session is None:
            print("❌ Não foi possível obter sessão Spark")
            print("💡 Certifique-se de que está executando em um notebook Databricks")
            print("💡 Ou em um ambiente com PySpark configurado")
            return
        
        # Mostrar informações da sessão
        session_info = SparkSessionManager.get_session_info()
        print(f"✅ Sessão Spark detectada: {session_info.get('version', 'N/A')}")
        if session_info.get('is_databricks'):
            print("✅ Ambiente Databricks detectado")
        
        # Usar spark_session 
        spark = spark_session
        
        print(f"🏢 Projeto: {project_name}")
        print(f"💾 Storage: {storage_name}")
        print(f"📁 Catálogo: {catalog_name}")
        print(f"📊 Schema: {schema_name}")
        
        # Verificar se o catálogo existe
        print(f"\n🔍 Verificando catálogo '{catalog_name}'...")
        try:
            spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
            print(f"✅ Catálogo '{catalog_name}' encontrado")
        except Exception as e:
            print(f"❌ Catálogo '{catalog_name}' não encontrado: {e}")
            return
        
        # Obter external location
        print(f"🔍 Obtendo external location para '{catalog_name}'...")
        try:
            external_location_result = spark.sql(f"DESCRIBE EXTERNAL LOCATION {catalog_name}").select("url").collect()
            if external_location_result:
                external_location = external_location_result[0].url
                schema_location = f"{external_location}/{catalog_name}/{schema_name}/"
                
                print(f"✅ External Location: {external_location}")
                print(f"✅ Schema Location: {schema_location}")
                
                # Criar schema
                print(f"\n📊 Criando schema '{catalog_name}.{schema_name}'...")
                spark.sql(f"""
                    CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
                    MANAGED LOCATION '{schema_location}'
                """)
                
                print(f"✅ Schema '{catalog_name}.{schema_name}' criado com sucesso!")
                
                # Configurar variáveis de ambiente
                config_manager = get_config_manager()
                config_data = {
                    'catalog_name': catalog_name,
                    'schema_name': schema_name,
                    'project_name': project_name,
                    'storage_name': storage_name,
                    'external_location': external_location,
                    'schema_location': schema_location
                }
                
                for key, value in config_data.items():
                    config_manager.set_variable(key.upper(), str(value))
                
                print(f"\n🎉 Configuração concluída!")
                print(f"   Projeto: {project_name}")
                print(f"   Storage: {storage_name}")
                print(f"   Catálogo: {catalog_name}")
                print(f"   Schema: {schema_name}")
                
            else:
                print(f"❌ External location não encontrada para catálogo '{catalog_name}'")
                
        except Exception as e:
            print(f"❌ Erro ao configurar schema: {e}")
            
    except ImportError:
        print("❌ Este comando deve ser executado no ambiente Databricks")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")


@config.command()
@click.option('--catalog-name', default='main', help='Nome do catálogo Unity Catalog (padrão: main)')
@click.option('--schema-name', default='default', help='Nome do schema (padrão: default)')
def validate(catalog_name: str, schema_name: str):
    """
    Validar configuração do DINO SDK

    Exemplos:
        dino-config validate
        dino-config validate --catalog-name vendas --schema-name bronze
    """
    print("🔍 Dino SDK - Validação de Configuração")
    print("=" * 45)
    
    try:
        # Usar SparkSessionManager para detecção robusta
        spark_session = SparkSessionManager.get_spark_session("DINO Config Validate")
        
        if spark_session is None:
            print("❌ Este comando deve ser executado no ambiente Databricks")
            return
        
        spark = spark_session
        
        print(f"📊 Validando catálogo: {catalog_name}")
        try:
            spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
            print(f"✅ Catálogo '{catalog_name}' existe")
        except Exception as e:
            print(f"❌ Catálogo '{catalog_name}' não encontrado: {e}")
            return
        
        print(f"📊 Validando schema: {catalog_name}.{schema_name}")
        try:
            spark.sql(f"DESCRIBE SCHEMA {catalog_name}.{schema_name}").collect()
            print(f"✅ Schema '{catalog_name}.{schema_name}' existe")
        except Exception as e:
            print(f"❌ Schema '{catalog_name}.{schema_name}' não encontrado: {e}")
            return
        
        print(f"\n🎉 Configuração validada com sucesso!")
        
    except ImportError:
        print("❌ Este comando deve ser executado no ambiente Databricks")
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


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
    
    # Agrupar configurações por categoria
    databricks_config = {}
    other_config = {}
    
    for key, value in config_dict.items():
        if any(db_key in key.lower() for db_key in ['catalog', 'checkpoint', 'volume', 'workspace']):
            databricks_config[key] = value
        else:
            other_config[key] = value
    
    # Mostrar configurações Databricks
    if databricks_config:
        for key, value in databricks_config.items():
            print(f"{key}: {value}")
    
    # Mostrar outras configurações
    if other_config:
        for key, value in other_config.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    if not config_dict:
        print("⚠️ Nenhuma configuração encontrada")
        print("💡 Execute 'dino-config setup' para configurar o SDK")


if __name__ == '__main__':
    config()
