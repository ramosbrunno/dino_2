#!/usr/bin/env python3
"""
Script de diagnóstico para Dino SDK no Databricks
Para usar: python diagnostic.py
"""

import sys
import os
import subprocess
import importlib
import pkg_resources

def run_diagnostic():
    """Execute diagnóstico completo do Dino SDK"""
    
    print("=" * 60)
    print("DIAGNÓSTICO DINO SDK - DATABRICKS")
    print("=" * 60)
    
    # 1. Informações do Python
    print(f"\n1. PYTHON ENVIRONMENT")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print(f"   Python path:")
    for path in sys.path:
        print(f"     - {path}")
    
    # 2. Verificar se dino-sdk está instalado
    print(f"\n2. PACKAGE INSTALLATION")
    try:
        import pkg_resources
        dist = pkg_resources.get_distribution('dino-sdk')
        print(f"   ✅ dino-sdk instalado: {dist.version}")
        print(f"   Localização: {dist.location}")
    except pkg_resources.DistributionNotFound:
        print(f"   ❌ dino-sdk NÃO ENCONTRADO")
        return
    
    # 3. Verificar entry points
    print(f"\n3. ENTRY POINTS")
    try:
        for ep in pkg_resources.iter_entry_points('console_scripts'):
            if 'dino' in ep.name:
                print(f"   ✅ {ep.name} -> {ep.module_name}:{ep.attrs[0]}")
    except Exception as e:
        print(f"   ❌ Erro verificando entry points: {e}")
    
    # 4. Verificar estrutura de arquivos
    print(f"\n4. FILE STRUCTURE")
    try:
        import src
        print(f"   ✅ src module importado: {src.__file__}")
    except ImportError as e:
        print(f"   ❌ Erro importando src: {e}")
    
    try:
        import src.config_cli
        print(f"   ✅ src.config_cli importado: {src.config_cli.__file__}")
    except ImportError as e:
        print(f"   ❌ Erro importando src.config_cli: {e}")
    
    # 5. Testar função config
    print(f"\n5. CONFIG FUNCTION TEST")
    try:
        from src.config_cli import config
        print(f"   ✅ Função config importada: {config}")
        
        # Testar se é uma função click
        if hasattr(config, '__call__'):
            print(f"   ✅ config é callable")
            if hasattr(config, 'commands'):
                print(f"   ✅ config tem comandos: {list(config.commands.keys())}")
            else:
                print(f"   ⚠️  config não tem atributo 'commands'")
        else:
            print(f"   ❌ config não é callable")
            
    except Exception as e:
        print(f"   ❌ Erro testando função config: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Verificar executáveis
    print(f"\n6. EXECUTABLE CHECK")
    try:
        result = subprocess.run(['which', 'dino-config'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ dino-config encontrado: {result.stdout.strip()}")
        else:
            print(f"   ❌ dino-config não encontrado no PATH")
    except Exception as e:
        print(f"   ❌ Erro verificando executável: {e}")
    
    # 7. Test manual execution
    print(f"\n7. MANUAL EXECUTION TEST")
    try:
        from src.config_cli import config
        print(f"   Tentando executar config(['--help'])...")
        config(['--help'])
    except SystemExit:
        print(f"   ✅ Comando executou (SystemExit é normal para --help)")
    except Exception as e:
        print(f"   ❌ Erro na execução manual: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("DIAGNÓSTICO COMPLETO")
    print("=" * 60)

if __name__ == "__main__":
    run_diagnostic()
