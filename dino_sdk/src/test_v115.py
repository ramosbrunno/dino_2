#!/usr/bin/env python3
"""
🧪 Teste CLI - DINO SDK v1.1.5 com Notebook Runner
"""

import argparse
import sys
from typing import Optional

def test_notebook_approach(notebook_path: Optional[str] = None):
    """
    Testa a abordagem com notebook runner
    
    Args:
        notebook_path: Caminho opcional para notebook customizado
    """
    print("🧪 TESTE DINO SDK v1.1.5 - Notebook Runner")
    print("=" * 55)
    
    try:
        # Importar módulo
        from keyvault_config_v115 import KeyVaultConfigWithNotebook
        
        print("✅ Módulo importado com sucesso")
        
        # Criar instância
        config = KeyVaultConfigWithNotebook()
        
        # Verificar ambiente
        if not config.is_databricks_environment():
            print("⚠️ Não está em ambiente Databricks")
            print("💡 Esta funcionalidade só funciona dentro do Databricks")
            return False
        
        # Executar teste completo
        success = config.test_connection(notebook_path)
        
        if success:
            print("\n🎉 SUCESSO: v1.1.5 funcionando!")
            return True
        else:
            print("\n❌ Falha nos testes")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_context_extraction(notebook_path: Optional[str] = None):
    """
    Testa apenas a extração de contexto
    """
    print("🔑 TESTE DE EXTRAÇÃO DE CONTEXTO")
    print("=" * 40)
    
    try:
        from keyvault_config_v115 import extract_databricks_context
        
        print("✅ Função de extração importada")
        
        # Extrair contexto
        context = extract_databricks_context(notebook_path, use_cache=False)
        
        if context:
            print("✅ Contexto extraído com sucesso!")
            print(f"📋 Método: {context.get('extraction_method', 'unknown')}")
            print(f"🌐 Workspace: {context.get('workspace_url', 'N/A')}")
            print(f"⏰ Timestamp: {context.get('timestamp', 'N/A')}")
            return True
        else:
            print("❌ Falha na extração")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simulate_usage():
    """
    Simula uso da nova versão
    """
    print("🎭 SIMULAÇÃO DE USO")
    print("=" * 25)
    
    print("📝 Código de exemplo:")
    print("""
# Uso simples
from src.keyvault_config_v115 import quick_setup

try:
    config = quick_setup()
    secrets = config.load_secrets_from_scope()
    print(f"✅ {len(secrets)} secrets carregados")
except Exception as e:
    print(f"❌ Erro: {e}")

# Uso com notebook customizado
from src.keyvault_config_v115 import KeyVaultConfigWithNotebook

config = KeyVaultConfigWithNotebook()
context = config.get_databricks_context(
    notebook_path="/my/custom/notebook"
)
secrets = config.load_secrets_from_scope(context)
    """)
    
    print("\n💡 Para usar:")
    print("1. Salve o notebook token_extractor.ipynb no Databricks")
    print("2. Execute: python test_v115.py --test-full")
    print("3. Ou use: python test_v115.py --extract-only")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="🧪 Teste DINO SDK v1.1.5 com Notebook Runner"
    )
    
    parser.add_argument(
        '--test-full',
        action='store_true',
        help='Executar teste completo (requer Databricks)'
    )
    
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Testar apenas extração de contexto'
    )
    
    parser.add_argument(
        '--notebook-path',
        type=str,
        help='Caminho customizado para notebook'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Apenas mostrar exemplo de uso'
    )
    
    args = parser.parse_args()
    
    if args.simulate:
        simulate_usage()
        return
    
    if args.test_full:
        success = test_notebook_approach(args.notebook_path)
        sys.exit(0 if success else 1)
    
    if args.extract_only:
        success = test_context_extraction(args.notebook_path)
        sys.exit(0 if success else 1)
    
    # Padrão: mostrar ajuda
    print("🚀 DINO SDK v1.1.5 - Notebook Runner")
    print("=" * 40)
    print("Nova abordagem usando notebook interno para extrair tokens")
    print("\nOpções:")
    print("  --test-full       Teste completo (requer Databricks)")
    print("  --extract-only    Apenas extração de contexto")
    print("  --simulate        Mostrar exemplo de uso")
    print("  --notebook-path   Caminho customizado para notebook")
    print("\nExemplos:")
    print("  python test_v115.py --simulate")
    print("  python test_v115.py --test-full")
    print("  python test_v115.py --extract-only --notebook-path /my/notebook")

if __name__ == "__main__":
    main()
