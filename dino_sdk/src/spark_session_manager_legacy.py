# spark_session_manager.py
"""
DINO SDK - Spark Session Manager (Legacy Compatibility)
Mantido apenas para compatibilidade com código existente
Recomenda-se usar SparkSession diretamente nas funções
"""

from pyspark.sql import SparkSession
import os


class SparkSessionManager:
    """
    Gerenciador de sessão Spark - LEGACY
    
    NOTA: Esta classe é mantida apenas para compatibilidade.
    Recomenda-se usar SparkSession diretamente como parâmetro nas funções.
    
    Exemplo recomendado:
        def minha_funcao(spark: SparkSession, outros_params):
            # usar spark diretamente
            return spark.sql("SELECT 1")
    """
    
    @staticmethod
    def create_spark_session(app_name):
        """Cria sessão Spark simples - LEGACY"""
        return SparkSession.builder.appName(app_name).getOrCreate()

    @staticmethod
    def get_spark_session(app_name="DINO SDK", force_create_for_cli=False):
        """Obtém sessão Spark - LEGACY"""
        return SparkSessionManager.create_spark_session(app_name)

    @staticmethod
    def is_databricks_environment():
        """Verifica ambiente Databricks via variáveis de ambiente"""
        return any('DATABRICKS' in key for key in os.environ.keys())

    @staticmethod
    def is_spark_connect():
        """Sempre retorna False - compatibilidade"""
        return False

    @staticmethod
    def get_session_info():
        """Retorna informações básicas da sessão"""
        try:
            spark = SparkSessionManager.get_spark_session()
            return {
                'version': spark.version,
                'is_databricks': SparkSessionManager.is_databricks_environment(),
                'is_spark_connect': False
            }
        except:
            return {
                'version': 'N/A',
                'is_databricks': SparkSessionManager.is_databricks_environment(),
                'is_spark_connect': False
            }
