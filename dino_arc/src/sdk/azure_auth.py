"""
Azure Authentication Module for Dino ARC
Handles Azure Service Principal authentication and credential management
"""

import os
import subprocess
import json
from typing import Dict, Optional, Any


class AzureAuth:
    """
    Classe para autenticação Azure via Service Principal
    """
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str, subscription_id: str):
        """
        Inicializa o Azure Auth com credenciais do Service Principal
        
        Args:
            client_id: Azure Client ID
            client_secret: Azure Client Secret  
            tenant_id: Azure Tenant ID
            subscription_id: Azure Subscription ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self._authenticated = False
        
    def authenticate(self) -> bool:
        """
        Autentica usando Service Principal e configura variáveis de ambiente
        
        Returns:
            bool: True se autenticação bem-sucedida
        """
        print("🔐 Autenticando com Azure via Service Principal...")
        
        try:
            # Configurar variáveis de ambiente para Terraform
            os.environ.update({
                'ARM_CLIENT_ID': self.client_id,
                'ARM_CLIENT_SECRET': self.client_secret,
                'ARM_TENANT_ID': self.tenant_id,
                'ARM_SUBSCRIPTION_ID': self.subscription_id
            })
            
            # Testar autenticação usando Azure CLI
            result = subprocess.run([
                'az', 'login', '--service-principal',
                '--username', self.client_id,
                '--password', self.client_secret,
                '--tenant', self.tenant_id
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Definir subscription ativa
                subprocess.run([
                    'az', 'account', 'set',
                    '--subscription', self.subscription_id
                ], capture_output=True, text=True, timeout=30)
                
                print("✅ Autenticação Azure realizada com sucesso!")
                self._authenticated = True
                return True
            else:
                print(f"❌ Erro na autenticação Azure: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout na autenticação Azure")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado na autenticação: {e}")
            return False
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Retorna variáveis de ambiente configuradas para Terraform
        
        Returns:
            Dict com variáveis de ambiente ARM_*
        """
        return {
            'ARM_CLIENT_ID': self.client_id,
            'ARM_CLIENT_SECRET': self.client_secret,
            'ARM_TENANT_ID': self.tenant_id,
            'ARM_SUBSCRIPTION_ID': self.subscription_id
        }
    
    def is_authenticated(self) -> bool:
        """
        Verifica se está autenticado
        
        Returns:
            bool: Status da autenticação
        """
        return self._authenticated
    
    def get_access_token(self) -> Optional[str]:
        """
        Obtém access token para APIs Azure
        
        Returns:
            str: Access token ou None se erro
        """
        try:
            result = subprocess.run([
                'az', 'account', 'get-access-token',
                '--resource', 'https://management.azure.com/'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                token_data = json.loads(result.stdout)
                return token_data.get('accessToken')
            else:
                print(f"❌ Erro ao obter access token: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter access token: {e}")
            return None
