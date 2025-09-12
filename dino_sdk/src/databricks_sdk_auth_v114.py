#!/usr/bin/env python3
"""
Dino SDK v1.1.4 - Autenticação Nativa via Databricks SDK
Usa autenticação automática do Databricks SDK em ambiente de runtime
"""

import logging
import os
from typing import Dict, Any, Optional

def get_databricks_auth_via_sdk():
    """
    Obtém autenticação usando Databricks SDK for Python com auto-detecção
    
    Returns:
        dict: {'workspace_url': str, 'token': str, 'client': WorkspaceClient} ou None
    """
    logger = logging.getLogger(__name__)
    
    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.core import Config
        
        logger.info("🔍 Tentando autenticação via Databricks SDK...")
        
        # Método 1: Autenticação automática no runtime
        try:
            # No ambiente Databricks, o SDK detecta automaticamente as credenciais
            client = WorkspaceClient()
            
            # Testar se a autenticação funcionou
            current_user = client.current_user.me()
            logger.info(f"✅ Autenticação SDK bem-sucedida - Usuário: {current_user.user_name}")
            
            # Extrair informações de configuração
            config = client.config
            workspace_url = config.host
            
            # O token pode não estar diretamente acessível, mas podemos usar o cliente
            context = {
                'workspace_url': workspace_url,
                'client': client,
                'user_info': current_user,
                'auth_method': 'databricks_sdk_auto'
            }
            
            logger.info(f"✅ Workspace URL: {workspace_url}")
            logger.info(f"✅ Usuário autenticado: {current_user.user_name}")
            return context
            
        except Exception as e:
            logger.error(f"❌ Autenticação automática falhou: {e}")
        
        # Método 2: Tentar com configuração explícita de runtime
        try:
            logger.info("🔍 Tentando configuração explícita de runtime...")
            
            # Buscar variáveis de ambiente específicas do Databricks
            databricks_runtime_version = os.getenv('DATABRICKS_RUNTIME_VERSION')
            spark_master = os.getenv('SPARK_MASTER', '')
            
            if databricks_runtime_version or 'local' not in spark_master.lower():
                logger.info(f"✅ Detectado ambiente Databricks (runtime: {databricks_runtime_version})")
                
                # Tentar configurar cliente com autenticação de runtime
                client = WorkspaceClient(
                    auth_type='databricks-cli'  # Usa credenciais do ambiente
                )
                
                # Testar autenticação
                current_user = client.current_user.me()
                workspace_url = client.config.host
                
                context = {
                    'workspace_url': workspace_url,
                    'client': client,
                    'user_info': current_user,
                    'auth_method': 'databricks_cli'
                }
                
                logger.info(f"✅ Autenticação CLI bem-sucedida")
                return context
                
        except Exception as e:
            logger.error(f"❌ Configuração explícita falhou: {e}")
        
        # Método 3: Tentar com Azure CLI (se disponível)
        try:
            logger.info("🔍 Tentando autenticação via Azure CLI...")
            
            client = WorkspaceClient(
                auth_type='azure-cli'
            )
            
            # Testar autenticação
            current_user = client.current_user.me()
            workspace_url = client.config.host
            
            context = {
                'workspace_url': workspace_url,
                'client': client,
                'user_info': current_user,
                'auth_method': 'azure_cli'
            }
            
            logger.info(f"✅ Autenticação Azure CLI bem-sucedida")
            return context
            
        except Exception as e:
            logger.error(f"❌ Autenticação Azure CLI falhou: {e}")
        
        # Método 4: Tentar detectar variáveis de ambiente
        try:
            logger.info("🔍 Tentando variáveis de ambiente...")
            
            host = os.getenv('DATABRICKS_HOST') or os.getenv('DATABRICKS_SERVER_HOSTNAME')
            token = os.getenv('DATABRICKS_TOKEN') or os.getenv('DATABRICKS_ACCESS_TOKEN')
            
            if host and token:
                logger.info(f"✅ Variáveis encontradas - Host: {host}")
                
                client = WorkspaceClient(
                    host=host,
                    token=token
                )
                
                # Testar autenticação
                current_user = client.current_user.me()
                
                context = {
                    'workspace_url': host,
                    'token': token,
                    'client': client,
                    'user_info': current_user,
                    'auth_method': 'environment_vars'
                }
                
                logger.info(f"✅ Autenticação por variáveis bem-sucedida")
                return context
                
        except Exception as e:
            logger.error(f"❌ Autenticação por variáveis falhou: {e}")
        
        logger.error("❌ Todas as estratégias de autenticação falharam")
        return None
        
    except ImportError as e:
        logger.error(f"❌ Databricks SDK não disponível: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro geral na autenticação: {e}")
        return None

def create_token_via_sdk(client, comment="Dino SDK Auto Token"):
    """
    Cria um token temporário usando o WorkspaceClient autenticado
    
    Args:
        client: WorkspaceClient autenticado
        comment: Comentário para o token
        
    Returns:
        str: Token gerado ou None se falhar
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Usar a API de tokens do SDK
        token_response = client.tokens.create(
            comment=comment,
            lifetime_seconds=3600  # 1 hora
        )
        
        token_value = token_response.token_value
        logger.info(f"✅ Token temporário criado: {token_value[:15]}...{token_value[-8:]}")
        return token_value
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar token: {e}")
        return None

def get_notebook_context_via_sdk():
    """
    Obtém contexto usando apenas Databricks SDK (sem dbutils)
    
    Returns:
        dict: Contexto completo ou None se falhar
    """
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Iniciando autenticação via Databricks SDK...")
    
    # Tentar autenticação
    auth_context = get_databricks_auth_via_sdk()
    
    if not auth_context:
        logger.error("❌ Falha na autenticação via SDK")
        return None
    
    client = auth_context['client']
    workspace_url = auth_context['workspace_url']
    
    # Se não temos token explícito, tentar criar um
    token = auth_context.get('token')
    if not token:
        logger.info("🔑 Token não disponível, tentando criar temporário...")
        token = create_token_via_sdk(client)
    
    # Montar contexto final
    context = {
        'workspace_url': workspace_url,
        'token': token,
        'client': client,
        'user_info': auth_context.get('user_info'),
        'auth_method': auth_context.get('auth_method'),
        'databricks_sdk': True
    }
    
    logger.info(f"✅ Contexto completo via SDK:")
    logger.info(f"   - Workspace: {workspace_url}")
    logger.info(f"   - Token: {'Disponível' if token else 'Não disponível'}")
    logger.info(f"   - Método: {auth_context.get('auth_method')}")
    
    return context

# Função de teste
def test_sdk_auth():
    """Testa autenticação via SDK"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando autenticação via Databricks SDK...")
    context = get_notebook_context_via_sdk()
    
    if context:
        print("✅ SUCESSO!")
        print(f"   - Workspace: {context.get('workspace_url')}")
        print(f"   - Token: {'***' if context.get('token') else 'N/A'}")
        print(f"   - Método: {context.get('auth_method')}")
        print(f"   - Usuário: {context.get('user_info', {}).get('user_name', 'N/A')}")
    else:
        print("❌ FALHOU!")
        
    return context
