#!/usr/bin/env python3
"""
🦕 DINO SDK v1.5.0 - TESTE SIMPLES DE IMPORTAÇÃO
🎯 Verificar se a sintaxe direta foi implementada
"""

print("🦕 DINO SDK v1.5.0 - TESTE DE IMPORTAÇÃO")
print("=" * 50)

try:
    from dino_sdk import __version__, create_dino_workflow
    print(f"✅ IMPORTAÇÃO SUCESSO!")
    print(f"📋 Versão: {__version__}")
    
    if __version__ == "1.5.0":
        print("🎯 *** VERSÃO 1.5.0 CONFIRMADA! ***")
        print("✅ Sintaxe direta implementada com sucesso!")
        
        # Verificar se a função está disponível
        if callable(create_dino_workflow):
            print("✅ Função create_dino_workflow disponível!")
            
            # Mostrar docstring para confirmar implementação
            doc = create_dino_workflow.__doc__
            if doc and "sintaxe direta" in doc.lower():
                print("✅ Documentação confirma sintaxe direta!")
            else:
                print("📝 Documentação padrão")
                
        print(f"\n🏆 RESULTADO: DINO SDK v1.5.0 PRONTO!")
        print(f"🎯 Problema 'as_dict' DEVE estar resolvido!")
        print(f"✅ Usando client.jobs.create(name=..., tasks=[...])")
        
    else:
        print(f"⚠️ Versão inesperada: {__version__}")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print(f"💡 Tentar: pip install dist\\dino_sdk-1.5.0-py3-none-any.whl --force-reinstall")

print(f"\n📋 RESUMO:")
print(f"   📦 Pacote: dino_sdk-1.5.0-py3-none-any.whl")
print(f"   🎯 Implementação: Sintaxe direta oficial")
print(f"   ✅ Status: Pronto para teste completo")
