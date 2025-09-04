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


@click.group()
def config():
    """Comandos de configuração do Dino SDK"""
    pass


@config.command()
@click.option('--project-name', required=True, help='Nome do projeto')
@click.option('--storage-name', required=True, help='Nome do Storage Account para External Location')
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
@click.option('--schema-name', required=True, help='Nome do schema destino (será criado se não existir)')
def setup(project_name: str, storage_name: str, catalog_name: str, schema_name: str):
    """
    Configuração simplificada do Dino SDK - Criação de Schema no Unity Catalog
    
    Este comando:
    1. Conecta ao workspace Databricks atual
    2. Verifica se o catálogo e external location existem
    3. Cria o schema no catálogo especificado
    4. Gera arquivo de configuração YAML no Volume
    
    IMPORTANTE: É necessário criar manualmente o Secret Scope antes de usar este comando.
    Para criar o Secret Scope, siga as instruções em:
    https://learn.microsoft.com/en-us/azure/databricks/security/secrets/
    
    Example:
        dino-config setup --project-name bronze --storage-name mystorageaccount --catalog-name vendas --schema-name bronze
    """
    print("🦕 Dino SDK - Configuração Simplificada")
    print("=" * 45)
    
    try:
        # Detectar ambiente Databricks e obter sessão Spark
        spark_session = None
        
        # Método 1: Tentar acessar variável global spark (Databricks)
        try:
            import builtins
            if hasattr(builtins, 'spark'):
                spark_session = builtins.spark
                print("✅ Detectado ambiente Databricks - usando sessão global")
        except:
            pass
        
        # Método 2: Tentar obter do contexto global atual
        if spark_session is None:
            try:
                # Acessar spark do contexto global
                import sys
                frame = sys._getframe(1)
                if 'spark' in frame.f_globals:
                    spark_session = frame.f_globals['spark']
                    print("✅ Sessão Spark encontrada no contexto global")
            except:
                pass
        
        # Método 3: Tentar criar/obter sessão ativa
        if spark_session is None:
            try:
                from pyspark.sql import SparkSession
                spark_session = SparkSession.getActiveSession()
                if spark_session:
                    print("✅ Sessão Spark ativa encontrada")
                else:
                    # Tentar obter do driver
                    from pyspark import SparkContext
                    if SparkContext._active_spark_context:
                        spark_session = SparkSession(SparkContext._active_spark_context)
                        print("✅ Sessão Spark criada a partir do contexto ativo")
            except Exception as e:
                print(f"⚠️ Erro ao obter sessão Spark via PySpark: {e}")
        
        # Método 4: Última tentativa - executar código para acessar spark
        if spark_session is None:
            try:
                # Tentar executar 'spark' diretamente
                exec_globals = {}
                exec('spark_session = spark', globals(), exec_globals)
                spark_session = exec_globals.get('spark_session')
                if spark_session:
                    print("✅ Sessão Spark obtida via execução direta")
            except:
                pass
        
        if spark_session is None:
            print("❌ Não foi possível obter sessão Spark")
            print("💡 Certifique-se de que está executando em um notebook Databricks")
            print("💡 Ou em um ambiente com PySpark configurado")
            return
        
        # Usar spark_session em vez de spark
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
            external_location = spark.sql(f"DESCRIBE EXTERNAL LOCATION {catalog_name}").select("url").collect()[0].url
            print(f"✅ External Location: {external_location}")
        except Exception as e:
            print(f"❌ Erro ao obter external location: {e}")
            return
        
        # Criar schema
        schema_location = f"{external_location}/{catalog_name}/{schema_name}/"
        print(f"\n� Criando schema '{catalog_name}.{schema_name}'...")
        print(f"� Localização: {schema_location}")
        
        try:
            spark.sql(f"""
                CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
                MANAGED LOCATION '{schema_location}'
            """)
            print(f"✅ Schema '{catalog_name}.{schema_name}' criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar schema: {e}")
            return
        
        # Criar configuração básica
        from .config_manager import get_config_manager
        
        config_manager = get_config_manager()
        config_updates = {
            'project_name': project_name,
            'storage_name': storage_name,
            'catalog_name': catalog_name,
            'schema_name': schema_name,
            'external_location': external_location,
            'schema_location': schema_location
        }
        
        config_manager.update_config(config_updates)
        
        print(f"\n🎉 Configuração concluída com sucesso!")
        print(f"📊 Schema: {catalog_name}.{schema_name}")
        print(f"📍 Localização: {schema_location}")
        print(f"\n⚠️  LEMBRETE: Crie manualmente o Secret Scope seguindo:")
        print(f"   https://learn.microsoft.com/en-us/azure/databricks/security/secrets/")
        
    except ImportError as e:
        print(f"❌ Dependências não instaladas: {e}")
        print("Este comando deve ser executado no ambiente Databricks")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")


@config.command()
def show():
    """Mostra configuração atual do Dino SDK"""
    print("🦕 Dino SDK - Configuração Atual")
    print("=" * 50)
    
    config_manager = get_config_manager()
    config_data = config_manager.show_config()
    
    if config_data:
        for key, value in config_data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    if 'password' in sub_key or 'key' in sub_key:
                        print(f"  {sub_key}: {'*' * 8}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            else:
                if 'password' in key or 'key' in key:
                    print(f"{key}: {'*' * 8}")
                else:
                    print(f"{key}: {value}")
    else:
        print("⚠️ Nenhuma configuração encontrada")
        print("💡 Execute: dino-config setup --help")


@config.command()
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
@click.option('--schema-name', required=True, help='Nome do schema a validar')
def validate(catalog_name: str, schema_name: str):
    """
    Valida se catálogo e schema existem no Unity Catalog
    
    Example:
        dino-config validate --catalog-name vendas --schema-name bronze
    """
    print("🔍 Dino SDK - Validação de Configuração")
    print("=" * 45)
    
    try:
        # Detectar ambiente Databricks e obter sessão Spark (mesmo método)
        spark_session = None
        
        # Método 1: Tentar acessar variável global spark (Databricks)
        try:
            import builtins
            if hasattr(builtins, 'spark'):
                spark_session = builtins.spark
        except:
            pass
        
        # Método 2: Tentar obter do contexto global atual
        if spark_session is None:
            try:
                import sys
                frame = sys._getframe(1)
                if 'spark' in frame.f_globals:
                    spark_session = frame.f_globals['spark']
            except:
                pass
        
        # Método 3: Tentar criar/obter sessão ativa
        if spark_session is None:
            try:
                from pyspark.sql import SparkSession
                spark_session = SparkSession.getActiveSession()
                if not spark_session:
                    from pyspark import SparkContext
                    if SparkContext._active_spark_context:
                        spark_session = SparkSession(SparkContext._active_spark_context)
            except:
                pass
        
        # Método 4: Última tentativa
        if spark_session is None:
            try:
                exec_globals = {}
                exec('spark_session = spark', globals(), exec_globals)
                spark_session = exec_globals.get('spark_session')
            except:
                pass
        
        if spark_session is None:
            print("❌ Não foi possível obter sessão Spark")
            print("💡 Execute em um notebook Databricks")
            return
        
        spark = spark_session
        
        print(f"📊 Validando catálogo: {catalog_name}")
        try:
            spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
            print(f"✅ Catálogo '{catalog_name}' existe")
        except Exception as e:
            print(f"❌ Catálogo '{catalog_name}' não encontrado: {e}")
            return
        
        print(f"� Validando schema: {catalog_name}.{schema_name}")
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


if __name__ == '__main__':
    config()
