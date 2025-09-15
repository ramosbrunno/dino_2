# spark_session_manager.py
from pyspark.sql import SparkSession


class SparkSessionManager:
    @staticmethod
    def create_spark_session(app_name):
        """
        Cria ou obtém uma sessão Spark.
        Creates or gets a Spark session.

        Args:
            app_name (str): Nome do aplicativo Spark.
                            Spark application name.

        Returns:
            SparkSession: A sessão Spark.
                        The Spark session.
        """
        return SparkSession.builder.appName(app_name).getOrCreate()

    @staticmethod
    def get_spark_session(app_name="DINO SDK", force_create_for_cli=False):
        """
        Obtém sessão Spark usando método simplificado.
        Gets Spark session using simplified method.

        Args:
            app_name (str): Nome do aplicativo.
            force_create_for_cli (bool): Ignorado - sempre usa getOrCreate.

        Returns:
            SparkSession: A sessão Spark.
        """
        return SparkSessionManager.create_spark_session(app_name)

    @staticmethod
    def is_databricks_environment():
        """
        Verifica se está em ambiente Databricks via variáveis de ambiente.
        Check if running in Databricks environment via environment variables.
        """
        import os
        return any('DATABRICKS' in key for key in os.environ.keys())

    @staticmethod
    def is_spark_connect():
        """
        Placeholder para compatibilidade - sempre retorna False.
        Placeholder for compatibility - always returns False.
        """
        return False

    @staticmethod
    def get_session_info():
        """
        Retorna informações básicas da sessão.
        Returns basic session information.
        """
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
