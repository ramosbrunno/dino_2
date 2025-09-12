#!/usr/bin/env python3
"""
Dino SDK - CLI Configuration Tool
Ferramenta de configuração via linha de comando do Dino SDK
"""

import click
import os
from .config_manager import get_config_manager
from .config_operations import ConfigOperations


def get_spark_session():
    """Tenta obter sessão Spark de forma simples"""
    try:
        from pyspark.sql import SparkSession
        
        # Método 1: Tentar sessão ativa
        spark = SparkSession.getActiveSession()
        if spark is not None:
            return spark
            
        # Método 2: Criar nova sessão simples
        return SparkSession.builder.appName("DINO SDK CLI").getOrCreate()
        
    except Exception as e:
        print(f"⚠️ Não foi possível criar sessão Spark: {str(e)[:100]}...")
        return None


def is_databricks_environment():
    """Verifica se está em ambiente Databricks via variáveis de ambiente"""
    return any('DATABRICKS' in key for key in os.environ.keys())


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
    
    # Agrupar configurações por categoria
    databricks_config = {}
    other_config = {}
    
    for key, value in config_dict.items():
        if any(db_key in key.lower() for db_key in ['catalog', 'checkpoint', 'volume', 'workspace']):
            databricks_config[key] = value
        else:
            other_config[key] = value
    
    # Mostrar configurações organizadamente
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


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
        print("🔍 Detectando ambiente Databricks...")
        
        is_databricks = is_databricks_environment()
        if is_databricks:
            print("✅ Ambiente Databricks detectado")
        else:
            print("⚠️ Ambiente Databricks não detectado")
        
        print("🔍 Tentando obter sessão Spark...")
        spark = get_spark_session()
        
        if spark is not None:
            print(f"✅ Sessão Spark obtida: {spark.version}")
            print(f"📊 Validando catálogo: {catalog_name}")
            
            # Usar ConfigOperations com spark como parâmetro
            result = ConfigOperations.validate_catalog_schema(spark, catalog_name, schema_name)
            
            if result['success']:
                print(f"\n🎉 Configuração validada com sucesso!")
            else:
                print(f"\n❌ Problemas encontrados na validação:")
                for error in result['errors']:
                    print(f"   • {error}")
        else:
            print("❌ Não foi possível criar sessão Spark")
            print("🔧 Tentando método alternativo...")
            
            # Usar método alternativo sem Spark
            result = ConfigOperations.validate_environment_alternative()
            
            if result['success']:
                print(f"\n🎯 Validação Alternativa Concluída!")
                print(f"   Catálogo alvo: {catalog_name}")
                print(f"   Schema alvo: {schema_name}")
                print(f"   Status: ✅ Ambiente Databricks confirmado")
            else:
                print(f"\n❌ Não foi possível validar configuração:")
                for error in result['errors']:
                    print(f"   • {error}")
        
    except ImportError:
        print("❌ Este comando deve ser executado no ambiente Databricks")
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


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
        print("🔍 Detectando ambiente Spark...")
        
        is_databricks = is_databricks_environment()
        if is_databricks:
            print("✅ Ambiente Databricks detectado")
        else:
            print("⚠️ Ambiente Databricks não detectado")
        
        print("🔍 Tentando obter sessão Spark...")
        spark = get_spark_session()
        
        if spark is not None:
            print(f"✅ Sessão Spark obtida: {spark.version}")
            print(f"🔧 Configurando Unity Catalog...")
            
            # Usar ConfigOperations com spark como parâmetro
            result = ConfigOperations.setup_unity_catalog(
                spark, project_name, storage_name, catalog_name, schema_name
            )
            
            if result['success']:
                print(f"\n🎉 Configuração concluída com sucesso!")
                print(f"   📁 Projeto: {project_name}")
                print(f"   📊 Catálogo: {catalog_name}")
                print(f"   📂 Schema: {schema_name}")
                print(f"   🗃️ Storage: {storage_name}")
            else:
                print(f"\n❌ Problemas na configuração:")
                for error in result['errors']:
                    print(f"   • {error}")
        else:
            print("❌ Não foi possível criar sessão Spark")
            print("🔧 Tentando configuração alternativa...")
            
            # Usar método alternativo sem Spark
            result = ConfigOperations.setup_environment_alternative(
                project_name, storage_name, catalog_name, schema_name
            )
            
            if result['success']:
                print(f"\n🎯 Configuração Alternativa Concluída!")
                print(f"   📁 Projeto: {project_name}")
                print(f"   📊 Catálogo: {catalog_name}")
                print(f"   📂 Schema: {schema_name}")
                print(f"   🗃️ Storage: {storage_name}")
            else:
                print(f"\n❌ Não foi possível configurar:")
                for error in result['errors']:
                    print(f"   • {error}")
        
    except ImportError:
        print("❌ Este comando deve ser executado no ambiente Databricks")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")


if __name__ == "__main__":
    config()
