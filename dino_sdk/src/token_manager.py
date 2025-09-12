#!/usr/bin/env python3
"""
🔑 Token Manager - DINO SDK v1.1.4
Gerenciador isolado para criação e teste de tokens Databricks
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class DatabricksTokenManager:
    """
    Gerenciador simplificado para tokens Databricks
    Foca apenas na criação de tokens sem dependências complexas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura logging simples"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def get_environment_config(self) -> Dict[str, Optional[str]]:
        """
        Obtém configuração do ambiente (variáveis de ambiente)
        
        Returns:
            Dicionário com configurações encontradas
        """
        config = {
            'DATABRICKS_HOST': os.getenv('DATABRICKS_HOST'),
            'DATABRICKS_TOKEN': os.getenv('DATABRICKS_TOKEN'),
            'AZURE_CLIENT_ID': os.getenv('AZURE_CLIENT_ID'),
            'AZURE_CLIENT_SECRET': os.getenv('AZURE_CLIENT_SECRET'),
            'AZURE_TENANT_ID': os.getenv('AZURE_TENANT_ID'),
        }
        
        self.logger.info("🔍 Verificando variáveis de ambiente...")
        for key, value in config.items():
            status = "✅" if value else "❌"
            masked_value = f"{value[:10]}..." if value and len(value) > 10 else value
            self.logger.info(f"   {status} {key}: {masked_value or 'não definida'}")
            
        return config
    
    def check_azure_cli_auth(self) -> bool:
        """
        Verifica se Azure CLI está autenticado
        
        Returns:
            True se autenticado, False caso contrário
        """
        try:
            import subprocess
            result = subprocess.run(
                ['az', 'account', 'show'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Azure CLI autenticado")
                return True
            else:
                self.logger.warning("❌ Azure CLI não autenticado")
                return False
                
        except FileNotFoundError:
            self.logger.warning("❌ Azure CLI não instalado")
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("⏱️ Timeout ao verificar Azure CLI")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar Azure CLI: {e}")
            return False
    
    def check_databricks_cli_auth(self) -> bool:
        """
        Verifica se Databricks CLI está configurado
        
        Returns:
            True se configurado, False caso contrário
        """
        try:
            import subprocess
            result = subprocess.run(
                ['databricks', 'fs', 'ls', '/'], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Databricks CLI configurado")
                return True
            else:
                self.logger.warning("❌ Databricks CLI não configurado")
                return False
                
        except FileNotFoundError:
            self.logger.warning("❌ Databricks CLI não instalado")
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("⏱️ Timeout ao verificar Databricks CLI")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar Databricks CLI: {e}")
            return False
    
    def create_token_with_environment_vars(self, lifetime_hours: int = 1) -> Optional[Dict[str, str]]:
        """
        Cria token usando variáveis de ambiente (DATABRICKS_HOST + credenciais)
        
        Args:
            lifetime_hours: Duração do token em horas
            
        Returns:
            Dicionário com token_id e access_token, ou None se falhar
        """
        config = self.get_environment_config()
        
        if not config['DATABRICKS_HOST']:
            self.logger.error("❌ DATABRICKS_HOST não definido")
            return None
        
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.core import Config
            
            workspace_url = config['DATABRICKS_HOST']
            if not workspace_url.startswith('https://'):
                workspace_url = f"https://{workspace_url}"
            
            self.logger.info(f"🔗 Conectando a: {workspace_url}")
            
            # Estratégia 1: Usar token existente (se disponível)
            if config['DATABRICKS_TOKEN']:
                self.logger.info("🔑 Usando DATABRICKS_TOKEN existente")
                client_config = Config(
                    host=workspace_url,
                    token=config['DATABRICKS_TOKEN']
                )
                client = WorkspaceClient(config=client_config)
                
            # Estratégia 2: Usar Service Principal
            elif all([config['AZURE_CLIENT_ID'], config['AZURE_CLIENT_SECRET'], config['AZURE_TENANT_ID']]):
                self.logger.info("🔑 Usando Service Principal")
                client_config = Config(
                    host=workspace_url,
                    azure_client_id=config['AZURE_CLIENT_ID'],
                    azure_client_secret=config['AZURE_CLIENT_SECRET'],
                    azure_tenant_id=config['AZURE_TENANT_ID']
                )
                client = WorkspaceClient(config=client_config)
                
            else:
                self.logger.error("❌ Credenciais insuficientes")
                self.logger.info("💡 Configure: DATABRICKS_TOKEN ou (AZURE_CLIENT_ID + AZURE_CLIENT_SECRET + AZURE_TENANT_ID)")
                return None
            
            # Testar conexão
            self.logger.info("🧪 Testando conexão...")
            current_user = client.current_user.me()
            self.logger.info(f"✅ Conectado como: {current_user.user_name}")
            
            # Criar token temporário
            self.logger.info(f"⏱️ Criando token temporário ({lifetime_hours}h)...")
            
            token_info = client.tokens.create(
                comment=f"DINO SDK Token - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                lifetime_seconds=lifetime_hours * 3600
            )
            
            expires_at = datetime.now() + timedelta(hours=lifetime_hours)
            
            result = {
                'token_id': token_info.token_id,
                'access_token': token_info.token_value,
                'expires_at': expires_at.isoformat(),
                'workspace_url': workspace_url,
                'created_by': current_user.user_name,
                'lifetime_hours': lifetime_hours
            }
            
            self.logger.info("🎉 Token criado com sucesso!")
            self.logger.info(f"   📋 Token ID: {token_info.token_id}")
            self.logger.info(f"   ⏰ Expira em: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar token: {e}")
            return None
    
    def create_token_with_azure_cli(self, workspace_url: str, lifetime_hours: int = 1) -> Optional[Dict[str, str]]:
        """
        Cria token usando Azure CLI para autenticação
        
        Args:
            workspace_url: URL do workspace Databricks
            lifetime_hours: Duração do token em horas
            
        Returns:
            Dicionário com token_id e access_token, ou None se falhar
        """
        if not self.check_azure_cli_auth():
            self.logger.error("❌ Azure CLI não autenticado. Execute: az login")
            return None
        
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.core import Config
            
            if not workspace_url.startswith('https://'):
                workspace_url = f"https://{workspace_url}"
            
            self.logger.info(f"🔗 Conectando via Azure CLI a: {workspace_url}")
            
            client_config = Config(
                host=workspace_url,
                auth_type='azure-cli'
            )
            client = WorkspaceClient(config=client_config)
            
            # Testar conexão
            self.logger.info("🧪 Testando conexão via Azure CLI...")
            current_user = client.current_user.me()
            self.logger.info(f"✅ Conectado como: {current_user.user_name}")
            
            # Criar token temporário
            self.logger.info(f"⏱️ Criando token temporário ({lifetime_hours}h)...")
            
            token_info = client.tokens.create(
                comment=f"DINO SDK Token (Azure CLI) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                lifetime_seconds=lifetime_hours * 3600
            )
            
            expires_at = datetime.now() + timedelta(hours=lifetime_hours)
            
            result = {
                'token_id': token_info.token_id,
                'access_token': token_info.token_value,
                'expires_at': expires_at.isoformat(),
                'workspace_url': workspace_url,
                'created_by': current_user.user_name,
                'auth_method': 'azure-cli',
                'lifetime_hours': lifetime_hours
            }
            
            self.logger.info("🎉 Token criado com sucesso via Azure CLI!")
            self.logger.info(f"   📋 Token ID: {token_info.token_id}")
            self.logger.info(f"   ⏰ Expira em: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar token via Azure CLI: {e}")
            return None
    
    def list_available_auth_methods(self) -> Dict[str, bool]:
        """
        Lista métodos de autenticação disponíveis
        
        Returns:
            Dicionário com métodos disponíveis
        """
        methods = {
            'environment_vars': bool(os.getenv('DATABRICKS_HOST')),
            'service_principal': all([
                os.getenv('AZURE_CLIENT_ID'),
                os.getenv('AZURE_CLIENT_SECRET'), 
                os.getenv('AZURE_TENANT_ID')
            ]),
            'existing_token': bool(os.getenv('DATABRICKS_TOKEN')),
            'azure_cli': self.check_azure_cli_auth(),
            'databricks_cli': self.check_databricks_cli_auth()
        }
        
        self.logger.info("🔍 Métodos de autenticação disponíveis:")
        for method, available in methods.items():
            status = "✅" if available else "❌"
            self.logger.info(f"   {status} {method}")
        
        return methods

def main():
    """Função principal para teste direto"""
    print("🔑 DINO SDK - Token Manager v1.1.4")
    print("=" * 50)
    
    manager = DatabricksTokenManager()
    
    # Listar métodos disponíveis
    print("\n📋 Verificando métodos de autenticação...")
    methods = manager.list_available_auth_methods()
    
    # Tentar criar token com métodos disponíveis
    workspace_url = os.getenv('DATABRICKS_HOST', 'your-workspace.azuredatabricks.net')
    
    print(f"\n🎯 Tentando criar token para: {workspace_url}")
    
    # Método 1: Variáveis de ambiente
    if methods['environment_vars']:
        print("\n1️⃣ Tentando com variáveis de ambiente...")
        token_result = manager.create_token_with_environment_vars(lifetime_hours=1)
        if token_result:
            print("✅ Token criado com sucesso!")
            return token_result
    
    # Método 2: Azure CLI
    if methods['azure_cli']:
        print("\n2️⃣ Tentando com Azure CLI...")
        token_result = manager.create_token_with_azure_cli(workspace_url, lifetime_hours=1)
        if token_result:
            print("✅ Token criado com sucesso!")
            return token_result
    
    print("\n❌ Nenhum método de autenticação funcionou")
    print("\n💡 Para resolver:")
    print("   1. Configure: export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net")
    print("   2. Configure: export DATABRICKS_TOKEN=your-token")
    print("   3. Ou execute: az login")
    
    return None

if __name__ == "__main__":
    main()
