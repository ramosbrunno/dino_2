#!/usr/bin/env python3
"""
🔑 CLI para Token Manager - DINO SDK v1.1.4
Comando isolado: dino-config get-token
"""

import argparse
import json
import sys
import os
from typing import Optional

def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description='🔑 DINO Token Manager - Criar e gerenciar tokens Databricks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Listar métodos disponíveis
  python -m src.token_cli list-auth

  # Criar token com variáveis de ambiente
  python -m src.token_cli get-token

  # Criar token via Azure CLI
  python -m src.token_cli get-token --method azure-cli --workspace https://workspace.azuredatabricks.net

  # Criar token com duração customizada
  python -m src.token_cli get-token --hours 8

Configuração necessária:
  
  Método 1 - Variáveis de ambiente:
    export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
    export DATABRICKS_TOKEN=your-existing-token
  
  Método 2 - Service Principal:
    export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
    export AZURE_CLIENT_ID=your-client-id
    export AZURE_CLIENT_SECRET=your-client-secret
    export AZURE_TENANT_ID=your-tenant-id
  
  Método 3 - Azure CLI:
    az login
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: list-auth
    list_parser = subparsers.add_parser(
        'list-auth', 
        help='Listar métodos de autenticação disponíveis'
    )
    
    # Comando: get-token
    token_parser = subparsers.add_parser(
        'get-token', 
        help='Criar um novo token Databricks'
    )
    token_parser.add_argument(
        '--method', 
        choices=['auto', 'env-vars', 'azure-cli'], 
        default='auto',
        help='Método de autenticação (padrão: auto)'
    )
    token_parser.add_argument(
        '--workspace', 
        help='URL do workspace Databricks (sobrescreve DATABRICKS_HOST)'
    )
    token_parser.add_argument(
        '--hours', 
        type=int, 
        default=1,
        help='Duração do token em horas (padrão: 1)'
    )
    token_parser.add_argument(
        '--output', 
        choices=['json', 'env', 'text'], 
        default='text',
        help='Formato de saída (padrão: text)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Importar token manager
    try:
        # Tentar importação relativa primeiro
        from token_manager import DatabricksTokenManager
    except ImportError:
        try:
            # Importação absoluta
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from token_manager import DatabricksTokenManager
        except ImportError:
            print("❌ Erro: Não foi possível importar DatabricksTokenManager")
            print("💡 Certifique-se de executar a partir do diretório correto")
            sys.exit(1)
    
    manager = DatabricksTokenManager()
    
    if args.command == 'list-auth':
        print("🔍 MÉTODOS DE AUTENTICAÇÃO DISPONÍVEIS")
        print("=" * 50)
        
        methods = manager.list_available_auth_methods()
        
        print("\n📊 Resumo:")
        available_count = sum(methods.values())
        print(f"   ✅ Métodos disponíveis: {available_count}/5")
        
        if available_count == 0:
            print("\n❌ Nenhum método de autenticação configurado!")
            print_setup_instructions()
        else:
            print(f"\n🎯 Recomendação: Execute 'get-token' para criar um token")
    
    elif args.command == 'get-token':
        print("🔑 CRIANDO TOKEN DATABRICKS")
        print("=" * 50)
        
        # Determinar workspace URL
        workspace_url = args.workspace or os.getenv('DATABRICKS_HOST')
        if not workspace_url:
            print("❌ Erro: URL do workspace não especificada")
            print("💡 Use --workspace ou configure DATABRICKS_HOST")
            sys.exit(1)
        
        # Criar token baseado no método
        token_result = None
        
        if args.method == 'auto':
            print("🎯 Método automático - tentando opções disponíveis...")
            
            # Tentar variáveis de ambiente primeiro
            token_result = manager.create_token_with_environment_vars(args.hours)
            
            # Se falhou, tentar Azure CLI
            if not token_result:
                print("\n🔄 Tentando Azure CLI...")
                token_result = manager.create_token_with_azure_cli(workspace_url, args.hours)
        
        elif args.method == 'env-vars':
            print("🎯 Usando variáveis de ambiente...")
            token_result = manager.create_token_with_environment_vars(args.hours)
        
        elif args.method == 'azure-cli':
            print("🎯 Usando Azure CLI...")
            token_result = manager.create_token_with_azure_cli(workspace_url, args.hours)
        
        # Exibir resultado
        if token_result:
            print("\n🎉 TOKEN CRIADO COM SUCESSO!")
            print("=" * 50)
            
            if args.output == 'json':
                print(json.dumps(token_result, indent=2))
            
            elif args.output == 'env':
                print(f"export DATABRICKS_HOST={token_result['workspace_url']}")
                print(f"export DATABRICKS_TOKEN={token_result['access_token']}")
            
            else:  # text
                print(f"📋 Token ID: {token_result['token_id']}")
                print(f"🔑 Access Token: {token_result['access_token'][:20]}...")
                print(f"🌐 Workspace: {token_result['workspace_url']}")
                print(f"⏰ Expira em: {token_result['expires_at']}")
                print(f"👤 Criado por: {token_result['created_by']}")
                
                print("\n💡 Para usar este token:")
                print(f"   export DATABRICKS_HOST={token_result['workspace_url']}")
                print(f"   export DATABRICKS_TOKEN={token_result['access_token']}")
        
        else:
            print("\n❌ FALHA AO CRIAR TOKEN")
            print("=" * 50)
            print_setup_instructions()
            sys.exit(1)

def print_setup_instructions():
    """Imprime instruções de configuração"""
    print("\n🔧 INSTRUÇÕES DE CONFIGURAÇÃO:")
    print("\n1️⃣ Opção 1 - Token existente:")
    print("   export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net")
    print("   export DATABRICKS_TOKEN=your-existing-token")
    
    print("\n2️⃣ Opção 2 - Service Principal:")
    print("   export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net")
    print("   export AZURE_CLIENT_ID=your-client-id")
    print("   export AZURE_CLIENT_SECRET=your-client-secret")
    print("   export AZURE_TENANT_ID=your-tenant-id")
    
    print("\n3️⃣ Opção 3 - Azure CLI:")
    print("   az login")
    print("   # Em seguida use: --workspace https://your-workspace.azuredatabricks.net")

if __name__ == '__main__':
    main()
