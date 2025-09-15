"""
DINO SDK - Schema Manager
Gerenciador de schemas para Unity Catalog seguindo padrão de receber spark como parâmetro
"""

from pyspark.sql import SparkSession
from typing import Dict, Any, Optional


class SchemaManager:
    """
    Gerenciador de schemas para Unity Catalog
    Segue o padrão de receber spark como parâmetro nas operações
    """
    
    def __init__(self, catalog: str, schema: str):
        """
        Inicializa o gerenciador de schema
        
        Args:
            catalog: Nome do catálogo Unity Catalog
            schema: Nome do schema
        """
        self.catalog = catalog
        self.schema = schema

    def catalog_exists(self, spark: SparkSession) -> bool:
        """
        Verifica se o catálogo existe
        
        Args:
            spark: Sessão Spark ativa
            
        Returns:
            True se catálogo existe, False caso contrário
        """
        try:
            result = spark.sql(f"SHOW CATALOGS LIKE '{self.catalog}'")
            return result.count() > 0
        except Exception as e:
            print(f"❌ Erro ao verificar catálogo '{self.catalog}': {e}")
            return False

    def schema_exists(self, spark: SparkSession) -> bool:
        """
        Verifica se o schema existe
        
        Args:
            spark: Sessão Spark ativa
            
        Returns:
            True se schema existe, False caso contrário
        """
        try:
            result = spark.sql(f"SHOW SCHEMAS IN {self.catalog} LIKE '{self.schema}'")
            return result.count() > 0
        except Exception as e:
            print(f"❌ Erro ao verificar schema '{self.schema}': {e}")
            return False

    def volume_exists(self, spark: SparkSession, volume_name: str, schema_name: str = None) -> bool:
        """
        Verifica se o volume existe
        
        Args:
            spark: Sessão Spark ativa
            volume_name: Nome do volume
            schema_name: Nome do schema (usa self.schema se não especificado)
            
        Returns:
            True se volume existe, False caso contrário
        """
        target_schema = schema_name if schema_name else self.schema
        
        try:
            result = spark.sql(f"SHOW VOLUMES IN {self.catalog}.{target_schema} LIKE '{volume_name}'")
            return result.count() > 0
        except Exception as e:
            print(f"❌ Erro ao verificar volume '{volume_name}': {e}")
            return False

    def create_volume(self, spark: SparkSession, volume_name: str, schema_name: str = None) -> Dict[str, Any]:
        """
        Cria um volume gerenciado no schema
        
        Args:
            spark: Sessão Spark ativa
            volume_name: Nome do volume a ser criado
            schema_name: Nome do schema (usa self.schema se não especificado)
            
        Returns:
            Dict com resultado da operação
        """
        target_schema = schema_name if schema_name else self.schema
        
        result = {
            'success': False,
            'volume_created': False,
            'already_exists': False,
            'errors': [],
            'volume_name': volume_name,
            'schema': target_schema
        }
        
        try:
            # Verificar se volume já existe
            if self.volume_exists(spark, volume_name, schema_name):
                result['already_exists'] = True
                result['success'] = True
                print(f"ℹ️ Volume '{volume_name}' já existe no schema {self.catalog}.{target_schema}")
                return result
            
            # Criar volume gerenciado
            create_sql = f"CREATE VOLUME {self.catalog}.{target_schema}.{volume_name}"
            
            print(f"📦 Criando volume gerenciado: {self.catalog}.{target_schema}.{volume_name}")
            spark.sql(create_sql)
            
            result['volume_created'] = True
            result['success'] = True
            
            print(f"✅ Volume '{volume_name}' criado com sucesso no schema {self.catalog}.{target_schema}")
            
        except Exception as e:
            error_msg = f"Erro ao criar volume '{volume_name}': {str(e)}"
            result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            
        return result

    def create_default_volumes(self, spark: SparkSession) -> Dict[str, Any]:
        """
        Cria os volumes padrão necessários para o DINO SDK
        
        Args:
            spark: Sessão Spark ativa
            
        Returns:
            Dict com resultado da operação
        """
        print(f"🔧 Criando volumes padrão para o schema {self.catalog}.{self.schema}")
        
        # Volumes padrão para o schema
        default_volumes = ['_checkpoints', '_schemas', 'raw']
        
        results = {
            'success': True,
            'volumes_created': [],
            'volumes_existing': [],
            'errors': []
        }
        
        for volume_name in default_volumes:
            result = self.create_volume(spark, volume_name)
            
            if result['success']:
                if result['volume_created']:
                    results['volumes_created'].append(volume_name)
                elif result['already_exists']:
                    results['volumes_existing'].append(volume_name)
            else:
                results['success'] = False
                results['errors'].extend(result['errors'])
        
        # Resumo
        if results['volumes_created']:
            print(f"✅ Volumes criados: {', '.join(results['volumes_created'])}")
        
        if results['volumes_existing']:
            print(f"ℹ️ Volumes já existentes: {', '.join(results['volumes_existing'])}")
        
        return results
        
        return results

    def get_external_location(self, spark: SparkSession) -> Optional[str]:
        """
        Obtém a localização externa do catálogo
        
        Args:
            spark: Sessão Spark ativa
            
        Returns:
            URL da localização externa ou None se não encontrada
        """
        try:
            result = spark.sql(f"DESCRIBE EXTERNAL LOCATION {self.catalog}")
            url_row = result.select("url").collect()
            if url_row:
                return url_row[0].url
            return None
        except Exception as e:
            print(f"⚠️ Não foi possível obter external location para '{self.catalog}': {e}")
            return None

    def create_schema(self, spark: SparkSession, managed_location: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria o schema no Unity Catalog
        
        Args:
            spark: Sessão Spark ativa
            managed_location: Localização gerenciada opcional (se não fornecida, usa external location)
            
        Returns:
            Dict com resultado da operação
        """
        result = {
            'success': False,
            'schema_created': False,
            'already_exists': False,
            'errors': [],
            'external_location': None
        }
        
        try:
            # Verificar se catálogo existe
            if not self.catalog_exists(spark):
                error_msg = f"Catálogo '{self.catalog}' não existe"
                result['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return result

            # Verificar se schema já existe
            if self.schema_exists(spark):
                result['already_exists'] = True
                result['success'] = True
                print(f"ℹ️ Schema '{self.schema}' já existe no catálogo {self.catalog}")
                return result
            
            # Obter external location se não foi fornecida managed location
            if managed_location is None:
                external_location = self.get_external_location(spark)
                if external_location:
                    managed_location = f"{external_location}/{self.catalog}/{self.schema}/"
                    result['external_location'] = external_location
            
            # Criar schema
            if managed_location:
                create_sql = f"""
                CREATE SCHEMA {self.catalog}.{self.schema} 
                MANAGED LOCATION '{managed_location}'
                """
                print(f"📁 Criando schema com localização gerenciada: {managed_location}")
            else:
                create_sql = f"CREATE SCHEMA {self.catalog}.{self.schema}"
                print(f"📁 Criando schema sem localização gerenciada especificada")
            
            spark.sql(create_sql)
            result['schema_created'] = True
            result['success'] = True
            
            print(f"✅ Schema '{self.schema}' criado com sucesso no catálogo {self.catalog}")
            
            # Criar volumes padrão após a criação do schema
            print(f"🔧 Criando volumes padrão para o schema...")
            volumes_result = self.create_default_volumes(spark)
            
            # Adicionar informações dos volumes ao resultado
            result['volumes_created'] = volumes_result.get('volumes_created', [])
            result['volumes_existing'] = volumes_result.get('volumes_existing', [])
            
            if not volumes_result['success']:
                print("⚠️ Alguns volumes não puderam ser criados, mas o schema foi criado com sucesso")
                result['volume_errors'] = volumes_result['errors']
            
        except Exception as e:
            error_msg = f"Erro ao criar schema: {str(e)}"
            result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            
        return result

    def ensure_schema_exists(self, spark: SparkSession, managed_location: Optional[str] = None) -> Dict[str, Any]:
        """
        Garante que o schema existe, criando se necessário
        
        Args:
            spark: Sessão Spark ativa
            managed_location: Localização gerenciada opcional
            
        Returns:
            Dict com resultado da operação
        """
        print(f"🔍 Verificando se schema {self.catalog}.{self.schema} existe...")
        
        if self.schema_exists(spark):
            print(f"✅ Schema {self.catalog}.{self.schema} já existe")
            
            # Verificar e criar volumes padrão se necessário
            print(f"🔍 Verificando volumes padrão...")
            volumes_result = self.create_default_volumes(spark)
            
            result = {
                'success': True,
                'schema_created': False,
                'already_exists': True,
                'errors': [],
                'volumes_created': volumes_result.get('volumes_created', []),
                'volumes_existing': volumes_result.get('volumes_existing', [])
            }
            
            if not volumes_result['success']:
                result['volume_errors'] = volumes_result['errors']
                print("⚠️ Alguns volumes não puderam ser criados")
                
            return result
        else:
            print(f"📁 Schema {self.catalog}.{self.schema} não existe, criando...")
            return self.create_schema(spark, managed_location)

    def get_schema_info(self, spark: SparkSession) -> Dict[str, Any]:
        """
        Obtém informações sobre o schema
        
        Args:
            spark: Sessão Spark ativa
            
        Returns:
            Dict com informações do schema
        """
        info = {
            'catalog': self.catalog,
            'schema': self.schema,
            'catalog_exists': False,
            'schema_exists': False,
            'external_location': None,
            'tables': [],
            'errors': []
        }
        
        try:
            info['catalog_exists'] = self.catalog_exists(spark)
            info['schema_exists'] = self.schema_exists(spark)
            
            if info['schema_exists']:
                # Listar tabelas no schema
                tables_df = spark.sql(f"SHOW TABLES IN {self.catalog}.{self.schema}")
                info['tables'] = [row.tableName for row in tables_df.collect()]
                
                # Obter external location se disponível
                info['external_location'] = self.get_external_location(spark)
                
        except Exception as e:
            error_msg = f"Erro ao obter informações do schema: {str(e)}"
            info['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            
        return info


# Função de conveniência para uso direto
def create_schema_simple(spark: SparkSession, catalog: str, schema: str, managed_location: Optional[str] = None) -> Dict[str, Any]:
    """
    Função de conveniência para criar schema sem instanciar classe
    
    Args:
        spark: Sessão Spark ativa
        catalog: Nome do catálogo
        schema: Nome do schema
        managed_location: Localização gerenciada opcional
        
    Returns:
        Dict com resultado da operação
    """
    manager = SchemaManager(catalog, schema)
    return manager.create_schema(spark, managed_location)


def ensure_schema_simple(spark: SparkSession, catalog: str, schema: str, managed_location: Optional[str] = None) -> Dict[str, Any]:
    """
    Função de conveniência para garantir que schema existe (com volumes)
    
    Args:
        spark: Sessão Spark ativa
        catalog: Nome do catálogo
        schema: Nome do schema
        managed_location: Localização gerenciada opcional
        
    Returns:
        Dict com resultado da operação
    """
    manager = SchemaManager(catalog, schema)
    return manager.ensure_schema_exists(spark, managed_location)


### Exemplo de uso:

# # Em um notebook Databricks (spark já disponível):
# from src.dino_sdk.schema_manager import SchemaManager, create_schema_simple
# 
# # Método 1: Usando a classe
# manager = SchemaManager("meu_catalogo", "meu_schema")
# result = manager.create_schema(spark)
# 
# # Método 2: Usando função de conveniência  
# result = create_schema_simple(spark, "meu_catalogo", "meu_schema")
# 
# # Verificar informações
# info = manager.get_schema_info(spark)
# print(f"Schema existe: {info['schema_exists']}")
# print(f"Tabelas: {info['tables']}")
