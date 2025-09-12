"""
🦕 DINO SDK v1.1.6 - Versão Simples para Databricks
Teste direto no Databricks notebook
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

def quick_databricks_test():
    """
    Teste rápido para executar no Databricks
    """
    print("🦕 DINO SDK v1.1.6 - Teste Direto no Databricks")
    print("=" * 60)
    
    # Teste 1: Verificar variáveis de ambiente
    print("\n1️⃣ Verificando variáveis de ambiente...")
    env_vars = [
        'DATABRICKS_RUNTIME_VERSION',
        'SPARK_HOME',
        'DATABRICKS_ROOT_VIRTUALIZATION_TYPE',
        'DATABRICKS_HOST',
        'DB_HOME'
    ]
    
    found_vars = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            found_vars.append(f"{var}={value[:50]}...")
            print(f"   ✅ {var}: {value[:50]}...")
        else:
            print(f"   ❌ {var}: não encontrado")
    
    if found_vars:
        print(f"✅ {len(found_vars)} variáveis Databricks encontradas")
    else:
        print("❌ Nenhuma variável Databricks encontrada")
    
    # Teste 2: Tentar acessar dbutils
    print("\n2️⃣ Testando acesso ao dbutils...")
    try:
        # Método 1: eval
        dbutils = eval('dbutils')
        if dbutils and hasattr(dbutils, 'notebook'):
            print("✅ dbutils encontrado via eval()")
            
            # Teste 3: Extrair token
            print("\n3️⃣ Extraindo token de administração...")
            try:
                admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
                if admin_token:
                    masked_token = f"{admin_token[:15]}...{admin_token[-8:]}"
                    print(f"✅ Token extraído: {masked_token}")
                    
                    # Teste 4: Extrair workspace URL
                    print("\n4️⃣ Extraindo URL do workspace...")
                    try:
                        workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
                        print(f"✅ Workspace URL: {workspace_url}")
                        
                        # Teste 5: Criar headers de autorização
                        print("\n5️⃣ Criando headers de autorização...")
                        headers = {"Authorization": f"Bearer {admin_token}"}
                        print("✅ Headers criados com sucesso")
                        
                        # Teste 6: Verificar secret scope
                        print("\n6️⃣ Testando acesso à secret scope...")
                        try:
                            scope_name = "dino-keyvault-scope"
                            # Tentar listar secrets
                            secrets = dbutils.secrets.list(scope_name)
                            print(f"✅ Secret scope '{scope_name}' acessível")
                            print(f"   📋 {len(secrets)} secrets encontrados")
                            
                            # Tentar carregar um secret de teste
                            for secret in secrets[:3]:  # Apenas os primeiros 3
                                secret_name = secret.key
                                try:
                                    secret_value = dbutils.secrets.get(scope_name, secret_name)
                                    if secret_value:
                                        print(f"   ✅ {secret_name}: carregado")
                                    else:
                                        print(f"   ⚠️ {secret_name}: vazio")
                                except Exception as e:
                                    print(f"   ❌ {secret_name}: erro {e}")
                            
                        except Exception as e:
                            print(f"❌ Erro ao acessar secret scope: {e}")
                        
                        print("\n🎉 TESTE COMPLETO FINALIZADO!")
                        print("✅ DINO SDK v1.1.6 está funcionando no Databricks")
                        
                        # Retornar contexto completo
                        return {
                            'admin_token': admin_token,
                            'workspace_url': workspace_url,
                            'headers': headers,
                            'dbutils': dbutils,
                            'environment_vars': found_vars,
                            'test_status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                    except Exception as e:
                        print(f"❌ Erro ao extrair workspace URL: {e}")
                        return None
                else:
                    print("❌ Token não encontrado")
                    return None
            except Exception as e:
                print(f"❌ Erro ao extrair token: {e}")
                return None
        else:
            print("❌ dbutils não tem atributo 'notebook'")
            return None
    except Exception as e:
        print(f"❌ dbutils não encontrado via eval(): {e}")
        
        # Tentar outros métodos
        print("\n   🔄 Tentando métodos alternativos...")
        
        # Método 2: globals
        if 'dbutils' in globals():
            print("✅ dbutils encontrado em globals()")
            return globals()['dbutils']
        else:
            print("❌ dbutils não está em globals()")
        
        # Método 3: Verificar PySpark
        try:
            import pyspark
            print("✅ PySpark disponível")
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                print("✅ SparkSession ativa encontrada")
            else:
                print("❌ Nenhuma SparkSession ativa")
        except Exception as e:
            print(f"❌ PySpark não disponível: {e}")
        
        return None

def simple_keyvault_config():
    """
    Configuração simples do KeyVault para Databricks
    """
    print("\n🔧 CONFIGURAÇÃO SIMPLES DO KEYVAULT")
    print("=" * 45)
    
    # Executar teste
    context = quick_databricks_test()
    
    if context and context.get('test_status') == 'success':
        print("\n✅ Contexto extraído com sucesso!")
        
        # Criar configuração simples
        config = {
            'keyvault_uri': "https://dino-keyvault-dev.vault.azure.net/",
            'secret_scope': "dino-keyvault-scope",
            'admin_token': context['admin_token'],
            'workspace_url': context['workspace_url'],
            'headers': context['headers'],
            'dbutils': context['dbutils']
        }
        
        print("🎯 Configuração criada e pronta para uso!")
        return config
    else:
        print("\n❌ Falha na configuração")
        return None

# Para uso direto no notebook Databricks
if __name__ == "__main__":
    # Executar teste
    config = simple_keyvault_config()
    
    if config:
        print("\n📦 CONFIGURAÇÃO DISPONÍVEL NA VARIÁVEL 'config'")
        print("💡 Use: config['dbutils'].secrets.get('dino-keyvault-scope', 'secret-name')")
    else:
        print("\n❌ Configuração falhou")
        print("💡 Verifique se está executando em um notebook Databricks")
