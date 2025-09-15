#!/usr/bin/env python3
"""
Utilitário para detectar e configurar ambiente Databricks notebook
"""

import os
import logging

def detect_databricks_environment():
    """
    Detecta se está executando em ambiente Databricks
    """
    indicators = {
        'spark_available': False,
        'runtime_version': None,
        'cluster_id': None,
        'conf_exists': False,
        'environment_vars': {}
    }
    
    # 1. Verificar se Spark está disponível
    try:
        import pyspark
        indicators['spark_available'] = True
    except ImportError:
        pass
    
    # 2. Verificar variáveis de ambiente específicas do Databricks
    databricks_vars = [
        'DATABRICKS_RUNTIME_VERSION',
        'DB_CLUSTER_ID', 
        'DATABRICKS_HOST',
        'DATABRICKS_TOKEN',
        'SPARK_HOME'
    ]
    
    for var in databricks_vars:
        value = os.getenv(var)
        if value:
            indicators['environment_vars'][var] = value
            if var == 'DATABRICKS_RUNTIME_VERSION':
                indicators['runtime_version'] = value
            elif var == 'DB_CLUSTER_ID':
                indicators['cluster_id'] = value
    
    # 3. Verificar arquivos de configuração
    config_paths = [
        '/databricks/spark/conf/spark-defaults.conf',
        '/opt/spark/conf/spark-defaults.conf'
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            indicators['conf_exists'] = True
            break
    
    return indicators

def get_databricks_client_for_notebook():
    """
    Obtém cliente Databricks otimizado para ambiente notebook
    """
    try:
        from databricks.sdk import WorkspaceClient
        
        # Estratégia específica para notebooks
        env_info = detect_databricks_environment()
        
        print("🔍 Informações do ambiente Databricks:")
        print(f"   Spark disponível: {env_info['spark_available']}")
        print(f"   Runtime version: {env_info['runtime_version']}")
        print(f"   Cluster ID: {env_info['cluster_id']}")
        print(f"   Configuração existe: {env_info['conf_exists']}")
        print(f"   Variáveis encontradas: {len(env_info['environment_vars'])}")
        
        # Abordagem 1: Auto-detecção simples
        try:
            client = WorkspaceClient()
            print("✅ WorkspaceClient() auto-detecção funcionou")
            return client
        except Exception as e:
            print(f"⚠️ Auto-detecção falhou: {e}")
        
        # Abordagem 2: Usar host se disponível
        host = os.getenv('DATABRICKS_HOST')
        if host:
            try:
                if not host.startswith('https://'):
                    host = f"https://{host}"
                client = WorkspaceClient(host=host)
                print(f"✅ WorkspaceClient com host {host} funcionou")
                return client
            except Exception as e:
                print(f"⚠️ Cliente com host falhou: {e}")
        
        # Abordagem 3: Tentar sem parâmetros mas com configuração explícita
        try:
            # No notebook, o cliente pode precisar de configuração especial
            client = WorkspaceClient(auth_type="default")
            print("✅ WorkspaceClient com auth_type='default' funcionou")
            return client
        except Exception as e:
            print(f"⚠️ Cliente com auth_type default falhou: {e}")
        
        raise Exception("Nenhuma abordagem de cliente funcionou")
        
    except ImportError:
        raise Exception("databricks-sdk não está disponível")

if __name__ == "__main__":
    # Teste local
    env_info = detect_databricks_environment()
    print("🔍 Teste de detecção do ambiente:")
    for key, value in env_info.items():
        print(f"   {key}: {value}")
