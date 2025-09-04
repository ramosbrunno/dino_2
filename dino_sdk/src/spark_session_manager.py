"""
DINO SDK - Spark Session Manager
Gerenciador inteligente de sessão Spark para diferentes ambientes

Suporta:
- Databricks (spark global variable)
- PySpark local
- Jupyter notebooks
- CLI environments
"""

from pyspark.sql import SparkSession
import logging
import inspect


class SparkSessionManager:
    """Gerenciador inteligente de sessão Spark para diferentes ambientes"""
    
    @staticmethod
    def get_databricks_spark():
        """Tenta obter a sessão Spark nativa do Databricks"""
        
        # Método 1: Variável global 'spark' (padrão Databricks)
        try:
            # Verificar se spark está em globals do frame atual ou superiores
            frame = inspect.currentframe()
            while frame:
                if 'spark' in frame.f_globals:
                    spark_session = frame.f_globals['spark']
                    if hasattr(spark_session, 'version'):
                        return spark_session
                frame = frame.f_back
        except:
            pass
            
        # Método 2: Verificar builtins
        try:
            import builtins
            if hasattr(builtins, 'spark'):
                return builtins.spark
        except:
            pass
            
        # Método 3: Exec com globals
        try:
            local_vars = {}
            exec("spark_session = spark", globals(), local_vars)
            spark_session = local_vars.get('spark_session')
            if spark_session and hasattr(spark_session, 'version'):
                return spark_session
        except:
            pass
            
        return None
    
    @staticmethod
    def get_active_session():
        """Obtém sessão ativa via SparkSession.getActiveSession()"""
        try:
            return SparkSession.getActiveSession()
        except:
            return None
    
    @staticmethod
    def create_new_session(app_name="DINO SDK"):
        """Cria nova sessão Spark (último recurso) - compatível com Spark Connect"""
        try:
            # Tentar criar sessão sem configurações específicas (compatível com Spark Connect)
            return SparkSession.builder.appName(app_name).getOrCreate()
        except Exception as e:
            logging.warning(f"Não foi possível criar nova sessão Spark: {e}")
            
            # Tentar com configuração mínima para Spark Connect
            try:
                return SparkSession.builder \
                    .appName(app_name) \
                    .config("spark.sql.adaptive.enabled", "false") \
                    .getOrCreate()
            except Exception as e2:
                logging.warning(f"Falha também com configuração mínima: {e2}")
                return None
    
    @classmethod
    def get_spark_session(cls, app_name="DINO SDK", prefer_databricks=True):
        """
        Obtém sessão Spark usando múltiplos métodos
        
        Args:
            app_name (str): Nome da aplicação Spark
            prefer_databricks (bool): Priorizar métodos Databricks
            
        Returns:
            SparkSession: Sessão Spark ou None se não conseguir
        """
        
        if prefer_databricks:
            # Priorizar métodos Databricks
            methods = [
                cls.get_databricks_spark,
                cls.get_active_session,
                lambda: cls.create_new_session(app_name)
            ]
        else:
            # Priorizar métodos genéricos
            methods = [
                cls.get_active_session,
                cls.get_databricks_spark,
                lambda: cls.create_new_session(app_name)
            ]
        
        for method in methods:
            try:
                session = method()
                if session:
                    return session
            except Exception as e:
                logging.debug(f"Método falhou: {method.__name__}: {e}")
                continue
        
        return None
    
    @classmethod
    def is_spark_connect(cls, session=None):
        """Verifica se está usando Spark Connect"""
        if session is None:
            session = cls.get_spark_session()
            
        if not session:
            return False
            
        try:
            # Tentar acessar sparkContext - se falhar, é Spark Connect
            _ = session.sparkContext.appName
            return False
        except Exception as e:
            # Se der erro sobre JVM_ATTRIBUTE_NOT_SUPPORTED, é Spark Connect
            if "JVM_ATTRIBUTE_NOT_SUPPORTED" in str(e) or "Spark Connect" in str(e):
                return True
            return False
    
    @classmethod
    def is_databricks_environment(cls):
        """Verifica se está executando no Databricks"""
        try:
            # Verificar dbutils
            import builtins
            if hasattr(builtins, 'dbutils'):
                return True
                
            # Verificar se existe a variável spark global
            spark_session = cls.get_databricks_spark()
            if spark_session:
                return True
                
            # Verificar contexto Databricks
            try:
                import dbruntime
                return True
            except ImportError:
                pass
                
        except:
            pass
            
        return False
    
    @classmethod
    def get_session_info(cls):
        """Retorna informações sobre a sessão Spark atual (compatível com Spark Connect)"""
        session = cls.get_spark_session()
        if not session:
            return {"status": "não encontrada"}
            
        try:
            info = {
                "status": "ativa",
                "version": session.version,
                "is_databricks": cls.is_databricks_environment(),
                "is_spark_connect": cls.is_spark_connect(session)
            }
            
            # Se for Spark Connect, não tentar acessar sparkContext
            if info["is_spark_connect"]:
                info["app_name"] = "Databricks Spark Connect"
                info["master"] = "spark-connect"
                info["connection_type"] = "spark-connect"
            else:
                # Tentar obter informações do SparkContext apenas se não for Spark Connect
                try:
                    info["app_name"] = session.sparkContext.appName
                    info["master"] = session.sparkContext.master
                    info["connection_type"] = "direct"
                except Exception:
                    info["app_name"] = "Spark Session"
                    info["master"] = "unknown"
                    info["connection_type"] = "unknown"
                    
            return info
            
        except Exception as e:
            return {"status": "erro", "error": str(e)}


def create_spark_session(app_name="DINO SDK"):
    """
    Função helper para criar/obter sessão Spark
    Compatível com o padrão sugerido pelo usuário
    """
    return SparkSessionManager.get_spark_session(app_name)


# Compatibilidade com código legado
def get_spark_session(app_name="DINO SDK"):
    """Alias para compatibilidade"""
    return create_spark_session(app_name)
