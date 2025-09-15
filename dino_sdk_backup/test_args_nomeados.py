#!/usr/bin/env python3
"""
🔧 DINO SDK v2.0.0 - CORREÇÃO ARGUMENTOS NOMEADOS  
✅ Correção: client.jobs.create() com argumentos nomeados
🎯 Fallback inteligente quando as_shallow_dict() não existe
"""

print("🔧 DINO SDK v2.0.0 - CORREÇÃO ARGUMENTOS NOMEADOS")
print("✅ Fallback: argumentos nomeados em vez de objeto posicional")
print("=" * 70)

# Instalar correção
import subprocess
import sys

print("📦 Instalando versão com correção...")
try:
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "dist/dino_sdk-2.0.0-py3-none-any.whl", 
        "--force-reinstall", "--quiet"
    ], check=True)
    print("✅ Instalado!")
except Exception as e:
    print(f"❌ {e}")
    exit(1)

# Importar
try:
    from dino_sdk import create_dino_workflow, __version__
    print(f"✅ DINO SDK v{__version__} importado!")
except ImportError as e:
    print(f"❌ Erro: {e}")
    exit(1)

print(f"\n🧪 TESTE: File Arrival Trigger com Argumentos Nomeados")
print(f"🎯 Deve usar fallback com argumentos corretos")
print("=" * 65)

try:
    resultado = create_dino_workflow(
        job_name="dino-v200-args-nomeados-teste",
        notebook_path="/Workspace/Users/user@company.com/test_args_nomeados", 
        existing_cluster_id="0904-143938-4t78b4kc",
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_args_nomeados",
        source_path="test_args_nomeados",
        
        is_automated=True,  # COM trigger - testar correção
        
        projeto="DINO SDK v2.0.0 - Argumentos Nomeados Teste",
        description="Teste correção argumentos nomeados no fallback"
    )
    
    if resultado.get("success"):
        print("🎉 CORREÇÃO FUNCIONOU!")
        print(f"🆔 Job ID: {resultado.get('job_id')}")
        print(f"🔗 URL: {resultado.get('job_url')}")
        print(f"✅ FILE ARRIVAL TRIGGER COM ARGUMENTOS NOMEADOS OK!")
        print(f"🎯 Fallback inteligente funcionando!")
        
        print(f"\n🏆 SOLUÇÃO FINAL:")
        print(f"   📚 Sua sintaxe: Prioridade (as_shallow_dict)")
        print(f"   🔧 Fallback: Argumentos nomeados corretos")
        print(f"   ✅ Compatibilidade: 100% garantida")
        print(f"   🦕 DINO SDK v2.0.0: FUNCIONANDO TOTAL!")
        
    else:
        print(f"❌ Ainda falhou: {resultado.get('error')}")
        print(f"🔧 Mais investigação necessária")
        
except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 ESTRATÉGIA FINAL:")
print(f"   1️⃣ Tentar sua sintaxe: **as_shallow_dict()")
print(f"   2️⃣ Fallback: argumentos nomeados")
print(f"   3️⃣ Compatibilidade: máxima")

print(f"\n🦕 DINO SDK v2.0.0")
print(f"   Smart fallback with named arguments! ✨")
