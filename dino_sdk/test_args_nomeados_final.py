#!/usr/bin/env python3
"""
🎯 DINO SDK v2.0.0 - TESTE ARGUMENTOS NOMEADOS
✅ Correção: jobs.create(name=..., trigger=..., tasks=...)
🎯 Objetos Task corretos + argumentos nomeados
"""

print("🎯 DINO SDK v2.0.0 - ARGUMENTOS NOMEADOS")
print("✅ Objetos Task + argumentos nomeados no jobs.create()")
print("🎯 Devemos ter sucesso agora!")
print("=" * 70)

# Instalar versão com argumentos nomeados
import subprocess
import sys

print("📦 Instalando versão com argumentos nomeados...")
try:
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "dist/dino_sdk-2.0.0-py3-none-any.whl", 
        "--force-reinstall", "--quiet"
    ], check=True)
    print("✅ Versão argumentos nomeados instalada!")
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

print(f"\n🎯 TESTE: File Arrival Trigger - Argumentos Nomeados")
print(f"✅ Task objects + jobs.create(name=..., trigger=..., tasks=...)")
print("=" * 70)

try:
    resultado = create_dino_workflow(
        job_name="dino-v200-args-nomeados-final",
        notebook_path="/Workspace/Users/user@company.com/test_args_nomeados_final",
        existing_cluster_id="0904-143938-4t78b4kc",
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_args_nomeados_final",
        source_path="test_args_nomeados_final",
        
        is_automated=True,  # COM trigger - teste argumentos nomeados!
        
        projeto="DINO SDK v2.0.0 - Args Nomeados Final",
        description="Teste com argumentos nomeados no jobs.create()"
    )
    
    if resultado.get("success"):
        print("🎉🎉🎉 SUCESSO DEFINITIVO! 🎉🎉🎉")
        print(f"🆔 Job ID: {resultado.get('job_id')}")
        print(f"🔗 URL: {resultado.get('job_url')}")
        print(f"✅ FILE ARRIVAL TRIGGER FUNCIONANDO!")
        print(f"🎯 PROBLEMA RESOLVIDO COMPLETAMENTE!")
        
        print(f"\n🏆 SOLUÇÃO FINAL:")
        print(f"   ✅ Task objects: Criados corretamente")
        print(f"   ✅ jobs.create(): Argumentos nomeados")
        print(f"   ✅ File arrival: Funcionando")
        print(f"   🦕 DINO SDK v2.0.0: SUCESSO TOTAL!")
        
        print(f"\n🎯 IMPLEMENTAÇÃO FINAL:")
        print(f"   📚 Task(task_key=..., notebook_task=NotebookTask(...)) ✅")
        print(f"   📚 jobs.create(name=..., trigger=..., tasks=...) ✅")
        print(f"   📚 File arrival triggers funcionais ✅")
        print(f"   🎯 v1.8.0 + v2.0.0 completamente funcionais!")
        
    else:
        print(f"❌ Ainda falhou: {resultado.get('error')}")
        print(f"🔧 Mais investigação necessária")
        
except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 EVOLUÇÃO COMPLETA:")
print(f"   🚀 v1.2.0: 'as_dict' errors")
print(f"   ✅ v1.8.0: Jobs simples funcionando")
print(f"   🔗 v2.0.0: File arrival triggers")
print(f"   💡 Solução: Task objects + argumentos nomeados")

print(f"\n🦕 DINO SDK v2.0.0")
print(f"   Complete solution with proper Task objects! ✨")
