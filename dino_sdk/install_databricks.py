#!/usr/bin/env python3
"""
Script de instalação para Databricks com diagnóstico
Inclui limpeza de cache e validação completa
"""

import subprocess
import sys
import os

def install_dino_sdk_databricks():
    """Instala Dino SDK no Databricks com diagnóstico completo"""
    
    print("🚀 INSTALAÇÃO DINO SDK NO DATABRICKS")
    print("=" * 50)
    
    # Etapa 1: Limpeza completa
    print("\n📦 Etapa 1: Limpeza de cache...")
    commands_cleanup = [
        "pip cache purge",
        "pip uninstall dino-sdk -y"
    ]
    
    for cmd in commands_cleanup:
        print(f"   Executando: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=False)
        except Exception as e:
            print(f"   ⚠️ Aviso: {e}")
    
    # Etapa 2: Instalação com força
    print("\n📥 Etapa 2: Instalação forçada...")
    wheel_url = "https://github.com/ramosbrunno/dino_2/releases/download/v1.0.1/dino_sdk-1.0.1-py3-none-any.whl"
    
    install_commands = [
        f"pip install --force-reinstall --no-deps --no-cache-dir {wheel_url}",
        "pip install --upgrade click databricks-sdk azure-identity azure-keyvault-secrets"
    ]
    
    for cmd in install_commands:
        print(f"   Executando: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"   ✅ Sucesso")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro: {e}")
            print(f"   Output: {e.stdout}")
            print(f"   Error: {e.stderr}")
    
    # Etapa 3: Diagnóstico
    print("\n🔍 Etapa 3: Diagnóstico...")
    
    try:
        # Verificar se foi instalado
        import pkg_resources
        dist = pkg_resources.get_distribution('dino-sdk')
        print(f"   ✅ dino-sdk {dist.version} instalado em: {dist.location}")
        
        # Verificar entry points
        for ep in pkg_resources.iter_entry_points('console_scripts'):
            if 'dino-config' == ep.name:
                print(f"   ✅ Entry point encontrado: {ep.name} -> {ep.module_name}:{ep.attrs[0]}")
                break
        else:
            print(f"   ❌ Entry point dino-config não encontrado")
        
        # Testar importação
        from src.config_cli import config
        print(f"   ✅ src.config_cli.config importado com sucesso")
        
        # Testar comandos
        if hasattr(config, 'commands'):
            commands = list(config.commands.keys())
            print(f"   ✅ Comandos disponíveis: {commands}")
        else:
            print(f"   ❌ Função config não tem comandos")
            
    except Exception as e:
        print(f"   ❌ Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    # Etapa 4: Teste final
    print("\n🧪 Etapa 4: Teste final...")
    
    try:
        result = subprocess.run(['dino-config', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ dino-config --help funcionou!")
            print(f"   Output: {result.stdout[:200]}...")
        else:
            print(f"   ❌ dino-config --help falhou:")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Erro executando dino-config: {e}")
    
    print("\n" + "=" * 50)
    print("✅ INSTALAÇÃO CONCLUÍDA")
    print("Execute: dino-config --help")
    print("=" * 50)

if __name__ == "__main__":
    install_dino_sdk_databricks()
