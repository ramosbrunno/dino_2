# config_operations.py
"""
DINO SDK - Configuration Operations
Operações de configuração que recebem spark como parâmetro
"""

import os
from typing import Dict, Any, Optional
from pyspark.sql import SparkSession
from .config_manager import get_config_manager


class ConfigOperations:
    """Operações de configuração seguindo padrão de receber spark como parâmetro"""
    
    @staticmethod
    def validate_catalog_schema(spark: SparkSession, catalog_name: str, schema_name: str) -> Dict[str, Any]:
        """
        Valida se catálogo e schema existem no Unity Catalog
        
        Args:
            spark: Sessão Spark ativa
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            Dict com resultado da validação
        """
        result = {
            'catalog_exists': False,
            'schema_exists': False,
            'errors': [],
            'success': False
        }
        
        try:
            # Validar catálogo
            spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
            result['catalog_exists'] = True
            print(f"✅ Catálogo '{catalog_name}' existe")
            
            # Validar schema
            try:
                schema_check = spark.sql(f"SHOW SCHEMAS IN {catalog_name} LIKE '{schema_name}'").collect()
                if len(schema_check) > 0:
                    result['schema_exists'] = True
                    print(f"✅ Schema '{catalog_name}.{schema_name}' existe")
                else:
                    result['errors'].append(f"Schema '{catalog_name}.{schema_name}' não encontrado")
                    print(f"❌ Schema '{catalog_name}.{schema_name}' não encontrado")
                    
            except Exception as e:
                # Fallback para método tradicional
                try:
                    spark.sql(f"DESCRIBE SCHEMA {catalog_name}.{schema_name}").collect()
                    result['schema_exists'] = True
                    print(f"✅ Schema '{catalog_name}.{schema_name}' existe")
                except Exception as e2:
                    result['errors'].append(f"Schema '{catalog_name}.{schema_name}' não encontrado: {str(e2)}")
                    print(f"❌ Schema '{catalog_name}.{schema_name}' não encontrado: {e2}")
            
            result['success'] = result['catalog_exists'] and result['schema_exists']
            
        except Exception as e:
            result['errors'].append(f"Catálogo '{catalog_name}' não encontrado: {str(e)}")
            print(f"❌ Catálogo '{catalog_name}' não encontrado: {e}")
            
        return result
    
    @staticmethod
    def setup_unity_catalog(
        spark: SparkSession, 
        project_name: str, 
        storage_name: str, 
        catalog_name: str, 
        schema_name: str
    ) -> Dict[str, Any]:
        """
        Configura Unity Catalog para o projeto
        
        Args:
            spark: Sessão Spark ativa
            project_name: Nome do projeto
            storage_name: Nome do storage account
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            Dict com resultado da configuração
        """
        result = {
            'schema_created': False,
            'tables_configured': False,
            'errors': [],
            'success': False
        }
        
        try:
            # Criar schema se não existir
            create_schema_sql = f"""
            CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
            COMMENT 'Schema criado pelo DINO SDK para projeto {project_name}'
            """
            
            spark.sql(create_schema_sql)
            result['schema_created'] = True
            print(f"✅ Schema '{catalog_name}.{schema_name}' criado/verificado")
            
            # Configurar localização base para tabelas
            config_manager = get_config_manager()
            
            # Atualizar configurações do projeto
            config_updates = {
                'project_name': project_name,
                'storage_name': storage_name,
                'catalog_name': catalog_name,
                'schema_name': schema_name,
                'checkpoint_base_path': f'/Volumes/{catalog_name}/{schema_name}/checkpoints/{project_name}',
                'volume_base_path': f'/Volumes/{catalog_name}/{schema_name}'
            }
            
            for key, value in config_updates.items():
                config_manager.set(key, value)
                
            result['tables_configured'] = True
            result['success'] = True
            
            print(f"✅ Configuração Unity Catalog concluída para projeto '{project_name}'")
            print(f"   📁 Catálogo: {catalog_name}")
            print(f"   📂 Schema: {schema_name}")
            print(f"   🗃️ Volumes: /Volumes/{catalog_name}/{schema_name}")
            
        except Exception as e:
            result['errors'].append(f"Erro na configuração: {str(e)}")
            print(f"❌ Erro na configuração: {e}")
            
        return result
    
    @staticmethod
    def validate_environment_alternative() -> Dict[str, Any]:
        """
        Validação alternativa sem Spark quando sessão não pode ser criada
        
        Returns:
            Dict com resultado da validação alternativa
        """
        result = {
            'is_databricks': False,
            'databricks_vars_found': 0,
            'can_validate': False,
            'errors': [],
            'success': False
        }
        
        try:
            # Verificar variáveis Databricks
            databricks_vars = [k for k in os.environ.keys() if 'DATABRICKS' in k]
            result['databricks_vars_found'] = len(databricks_vars)
            
            if databricks_vars:
                result['is_databricks'] = True
                result['can_validate'] = True
                result['success'] = True
                
                print("✅ Variáveis Databricks detectadas no ambiente")
                print(f"📋 Variáveis Databricks encontradas: {len(databricks_vars)}")
                print(f"✅ Ambiente Databricks confirmado via variáveis de sistema")
                print(f"⚠️ Nota: Validação limitada devido à falha na criação de sessão Spark")
                print(f"💡 Para validação completa, execute em um notebook Databricks")
            else:
                result['errors'].append("Nenhuma variável Databricks encontrada")
                print("❌ Não foi possível confirmar ambiente Databricks")
                print("💡 Dica: Execute este comando diretamente em um notebook Databricks")
                
        except Exception as e:
            result['errors'].append(f"Erro na validação alternativa: {str(e)}")
            print(f"❌ Método alternativo falhou: {e}")
            
        return result
    
    @staticmethod
    def setup_environment_alternative(
        project_name: str, 
        storage_name: str, 
        catalog_name: str, 
        schema_name: str
    ) -> Dict[str, Any]:
        """
        Configuração alternativa sem Spark quando sessão não pode ser criada
        
        Returns:
            Dict com resultado da configuração alternativa
        """
        result = {
            'config_updated': False,
            'databricks_confirmed': False,
            'errors': [],
            'success': False
        }
        
        try:
            # Verificar se estamos em ambiente Databricks
            databricks_vars = [k for k in os.environ.keys() if 'DATABRICKS' in k]
            
            if databricks_vars:
                result['databricks_confirmed'] = True
                
                # Atualizar configurações mesmo sem Spark
                config_manager = get_config_manager()
                config_updates = {
                    'project_name': project_name,
                    'storage_name': storage_name,
                    'catalog_name': catalog_name,
                    'schema_name': schema_name,
                    'checkpoint_base_path': f'/Volumes/{catalog_name}/{schema_name}/checkpoints/{project_name}',
                    'volume_base_path': f'/Volumes/{catalog_name}/{schema_name}'
                }
                
                for key, value in config_updates.items():
                    config_manager.set(key, value)
                    
                result['config_updated'] = True
                result['success'] = True
                
                print("✅ Configurações salvas localmente")
                print(f"   📁 Projeto: {project_name}")
                print(f"   🗃️ Storage: {storage_name}")
                print(f"   📊 Catálogo: {catalog_name}")
                print(f"   📂 Schema: {schema_name}")
                print(f"⚠️ Nota: Schema não foi criado no Unity Catalog (requer sessão Spark)")
                print(f"💡 Para criar schema, execute 'spark.sql(\"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}\")' em um notebook")
                
            else:
                result['errors'].append("Ambiente Databricks não confirmado")
                print("❌ Não foi possível confirmar ambiente Databricks")
                print("💡 Dica: Execute este comando diretamente em um notebook Databricks")
                
        except Exception as e:
            result['errors'].append(f"Erro na configuração alternativa: {str(e)}")
            print(f"❌ Configuração alternativa falhou: {e}")
            
        return result
