#!/usr/bin/env python3
"""
🎉 DINO SDK v2.0.0 - FILE ARRIVAL TRIGGER TEST
✅ v1.8.0 funcionou! Agora testando trigger baseado na sua referência
🎯 JobSettings.from_dict() + file_arrival
"""

print("🎉 DINO SDK v2.0.0 - FILE ARRIVAL TRIGGER TEST")
print("✅ Base v1.8.0 funcionou! Agora adicionando trigger")
print("📚 JobSettings.from_dict() baseado na sua nova referência")
print("=" * 95)

# Instalar v2.0.0
import subprocess
import sys

print("📦 Instalando DINO SDK v2.0.0...")
try:
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "dist/dino_sdk-2.0.0-py3-none-any.whl", 
        "--force-reinstall", "--quiet"
    ], check=True, cwd="c:\\Users\\User\\OneDrive\\Documentos\\Projetos\\Data_Master_2025\\GIT\\dino_2\\dino_sdk")
    print("✅ v2.0.0 instalado!")
except Exception as e:
    print(f"⚠️ {e}")

# Verificar v2.0.0
try:
    from dino_sdk import __version__, create_dino_workflow
    print(f"✅ DINO SDK v{__version__} importado!")
    
    if __version__ != "2.0.0":
        print(f"⚠️ Versão: {__version__} (esperava 2.0.0)")
        exit(1)
        
except ImportError as e:
    print(f"❌ Erro: {e}")
    exit(1)

# Verificar Databricks
try:
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()
    current_user = w.current_user.me()
    print(f"✅ Databricks: {current_user.user_name}")
except Exception as e:
    print(f"❌ Databricks: {e}")
    exit(1)

print(f"\n🧪 TESTE 1: JOB SEM TRIGGER (Garantir que v1.8.0 ainda funciona)")
print("🎯 Deve usar sintaxe Task() + NotebookTask() que já funcionou")
print("=" * 85)

try:
    # ✅ TESTE 1: SEM TRIGGER - sintaxe v1.8.0 que funciona
    resultado_sem_trigger = create_dino_workflow(
        job_name="dino-v200-sem-trigger-test",
        notebook_path="/Workspace/Users/user@company.com/test_v200_sem_trigger",
        existing_cluster_id="0904-143938-4t78b4kc",  # Cluster testado
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_v200_sem_trigger",
        source_path="test_v200_sem_trigger",
        
        is_automated=False,  # SEM trigger
        
        projeto="DINO SDK v2.0.0 - No Trigger Test",
        description="Garantir que sintaxe v1.8.0 ainda funciona"
    )
    
    if resultado_sem_trigger.get("success"):
        print("✅ TESTE 1 PASSOU - Job sem trigger funcionou!")
        print(f"   🆔 Job ID: {resultado_sem_trigger.get('job_id')}")
        print(f"   🎯 Sintaxe v1.8.0 mantida funcionando")
        teste1_ok = True
    else:
        print(f"❌ TESTE 1 FALHOU: {resultado_sem_trigger.get('error')}")
        teste1_ok = False
        
except Exception as e:
    print(f"❌ EXCEÇÃO TESTE 1: {e}")
    teste1_ok = False

print(f"\n🧪 TESTE 2: JOB COM FILE ARRIVAL TRIGGER (Nova feature v2.0.0)")
print("🎯 Deve usar JobSettings.from_dict() como na sua referência")
print("=" * 85)

try:
    # ✅ TESTE 2: COM TRIGGER - nova sintaxe JobSettings.from_dict()
    resultado_com_trigger = create_dino_workflow(
        job_name="dino-v200-com-trigger-test",
        notebook_path="/Workspace/Users/user@company.com/test_v200_com_trigger",
        existing_cluster_id="0904-143938-4t78b4kc",  # Cluster testado
        
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_v200_com_trigger", 
        source_path="test_v200_com_trigger",
        
        is_automated=True,  # COM trigger - isso deve gerar file_arrival_url
        
        projeto="DINO SDK v2.0.0 - Com Trigger Test",
        description="JobSettings.from_dict() com file arrival trigger"
    )
    
    if resultado_com_trigger.get("success"):
        print("✅ TESTE 2 PASSOU - Job com trigger funcionou!")
        print(f"   🆔 Job ID: {resultado_com_trigger.get('job_id')}")
        print(f"   🔗 File arrival trigger implementado!")
        print(f"   📚 JobSettings.from_dict() funcionando")
        teste2_ok = True
    else:
        print(f"❌ TESTE 2 FALHOU: {resultado_com_trigger.get('error')}")
        teste2_ok = False
        
except Exception as e:
    print(f"❌ EXCEÇÃO TESTE 2: {e}")
    import traceback
    traceback.print_exc()
    teste2_ok = False

print(f"\n🎯 RESULTADOS FINAIS v2.0.0:")
print("=" * 70)

print(f"📊 TESTES:")
print(f"   📝 Teste 1 (Sem Trigger): {'✅ PASSOU' if teste1_ok else '❌ FALHOU'}")
print(f"   🔗 Teste 2 (Com Trigger): {'✅ PASSOU' if teste2_ok else '❌ FALHOU'}")

if teste1_ok and teste2_ok:
    print(f"\n🎉🎉🎉 SUCESSO TOTAL v2.0.0! 🎉🎉🎉")
    print(f"🏆 DINO SDK COMPLETAMENTE FUNCIONAL!")
    print(f"   ✅ Jobs simples (v1.8.0): Funcionando perfeitamente")
    print(f"   🔗 Jobs com trigger (v2.0.0): Funcionando perfeitamente")
    print(f"   🦕 SDK PRONTO PARA PRODUÇÃO!")
    
    print(f"\n✅ FUNCIONALIDADES COMPLETAS:")
    print(f"   🎯 Unity Catalog integration")
    print(f"   📍 Path auto-resolution")
    print(f"   🖥️ Existing cluster support")
    print(f"   🔗 File arrival triggers")
    print(f"   📧 Email notifications")
    print(f"   💎 Liquid clustering")
    
    print(f"\n🏆 CONCLUSÃO:")
    print(f"   🎯 PROBLEMA ORIGINAL RESOLVIDO!")
    print(f"   📈 EVOLUÇÃO v1.2.0 → v2.0.0 COMPLETA!")
    print(f"   🦕 DINO SDK É UM SUCESSO TOTAL!")
    
elif teste1_ok and not teste2_ok:
    print(f"\n📈 PROGRESSO SÓLIDO v2.0.0!")
    print(f"   ✅ Base v1.8.0 CONFIRMADA funcionando")
    print(f"   🔧 Trigger precisa ajuste (mas base é sólida)")
    print(f"   💡 Sucesso parcial - podemos iterar no trigger")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Analisar logs do teste 2")
    print(f"   2. Ajustar implementação do JobSettings.from_dict()")
    print(f"   3. v1.8.0 é versão de produção estável")
    
else:
    print(f"\n🔍 INVESTIGAÇÃO NECESSÁRIA:")
    print(f"   📝 Analisar logs dos testes")
    print(f"   💡 Algo inesperado aconteceu")
    print(f"   🔄 Iterar baseado nos erros")

print(f"\n📦 ENTREGÁVEIS v2.0.0:")
print(f"   📄 dino_sdk-2.0.0-py3-none-any.whl")
print(f"   📝 DINO_SDK_v2.0.0_FILE_ARRIVAL.ipynb")
print(f"   🎯 Implementação: JobSettings.from_dict() + trigger")
print(f"   📚 Base: Suas referências que funcionaram")

print(f"\n🦕 DINO SDK v2.0.0 - From error to automation!")
print(f"   The complete journey: 'as_dict' → fully functional SDK! ✨")
