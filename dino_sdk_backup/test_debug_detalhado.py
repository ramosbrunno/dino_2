#!/usr/bin/env python3
"""
🔍 DINO SDK v2.0.0 - DEBUG DETALHADO
✅ Logging passo-a-passo para encontrar o problema exato
"""

print("🔍 DINO SDK v2.0.0 - DEBUG DETALHADO")
print("✅ Vamos encontrar exatamente onde está o problema!")
print("=" * 70)

# Instalar versão debug
import subprocess
import sys

print("📦 Instalando versão debug...")
try:
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "dist/dino_sdk-2.0.0-py3-none-any.whl", 
        "--force-reinstall", "--quiet"
    ], check=True)
    print("✅ Versão debug instalada!")
except Exception as e:
    print(f"❌ {e}")
    exit(1)

# Importar
try:
    from dino_sdk import create_dino_workflow, __version__
    print(f"✅ DINO SDK v{__version__} importado!")
except ImportError as e:
    print(f"❌ Erro import: {e}")
    exit(1)

print(f"\n🧪 TESTE DEBUG: File Arrival Trigger")
print(f"🔍 Logging detalhado ativado - vamos ver cada passo!")
print("=" * 70)

try:
    resultado = create_dino_workflow(
        job_name="dino-v200-debug-detalhado",
        notebook_path="/Workspace/Users/user@company.com/test_debug_detalhado",
        existing_cluster_id="0904-143938-4t78b4kc",
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_debug_detalhado",
        source_path="test_debug_detalhado",
        
        is_automated=True,  # COM trigger - debug completo
        
        projeto="DINO SDK v2.0.0 - Debug Detalhado",
        description="Debug passo-a-passo para encontrar o problema"
    )
    
    if resultado.get("success"):
        print("🎉 DEBUG SUCESSO!")
        print(f"🆔 Job ID: {resultado.get('job_id')}")
        print(f"🔗 URL: {resultado.get('job_url')}")
        print(f"✅ PROBLEMA RESOLVIDO COM DEBUG!")
    else:
        print(f"❌ DEBUG FALHOU: {resultado.get('error')}")
        print(f"🔍 Mas agora temos logs detalhados!")
        
except Exception as e:
    print(f"❌ EXCEÇÃO DEBUG: {e}")
    import traceback
    traceback.print_exc()
    print(f"\n🔍 ANÁLISE DO ERRO:")
    print(f"   📝 Veja os logs INFO acima")
    print(f"   🎯 Identifique qual PASSO falhou")
    print(f"   💡 Agora sabemos exatamente onde está o problema!")

print(f"\n🎯 DEBUG STEPS:")
print(f"   PASSO 1: Criar job_data dict")
print(f"   PASSO 2: Job.from_dict(job_data)")
print(f"   PASSO 3: Verificar métodos disponíveis")
print(f"   PASSO 4: Chamar as_dict()")
print(f"   PASSO 5: Criar job com **result")

print(f"\n🦕 DINO SDK v2.0.0 - Debug mode activated! 🔍")
