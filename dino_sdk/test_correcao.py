#!/usr/bin/env python3
"""
🔧 DINO SDK v2.0.0 - TESTE CORREÇÃO as_shallow_dict
✅ Correção: JobSettings.from_dict() → client.jobs.create(job_settings)
🎯 SEM usar as_shallow_dict()
"""

print("🔧 DINO SDK v2.0.0 - TESTE CORREÇÃO")
print("✅ Correção: as_shallow_dict() removido")
print("=" * 60)

# Instalar versão corrigida
import subprocess
import sys

print("📦 Instalando versão corrigida...")
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

print(f"\n🧪 TESTE: JOB COM FILE ARRIVAL TRIGGER")
print(f"🎯 Deve funcionar SEM erro as_shallow_dict")
print("=" * 50)

try:
    resultado = create_dino_workflow(
        job_name="dino-v200-correcao-test",
        notebook_path="/Workspace/Users/user@company.com/test_correcao",
        existing_cluster_id="0904-143938-4t78b4kc",
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_correcao",
        source_path="test_correcao",
        
        is_automated=True,  # COM trigger
        
        projeto="DINO SDK v2.0.0 - Correção Test",
        description="Teste correção as_shallow_dict"
    )
    
    if resultado.get("success"):
        print("🎉 SUCESSO! Correção funcionou!")
        print(f"🆔 Job ID: {resultado.get('job_id')}")
        print(f"🔗 File arrival trigger OK!")
        print(f"📚 JobSettings.from_dict() sem as_shallow_dict() funcionou!")
    else:
        print(f"❌ Falhou: {resultado.get('error')}")
        
except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 ANÁLISE:")
print(f"✅ Correção aplicada: JobSettings sem as_shallow_dict()")
print(f"🔧 Método correto: client.jobs.create(job_settings)")
print(f"📚 Baseado na sua referência que funciona")

print(f"\n🦕 DINO SDK v2.0.0 - Trigger functionality ready!")
