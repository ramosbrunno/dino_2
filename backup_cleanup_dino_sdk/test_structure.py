#!/usr/bin/env python3
"""
Dino SDK - Teste Simples
Verifica se a estrutura simplificada está funcionando
"""

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports do Dino SDK...")
    
    try:
        from ingestion_engine import IngestionEngine
        print("✅ IngestionEngine importado com sucesso")
        
        from workflow_manager import WorkflowManager
        print("✅ WorkflowManager importado com sucesso")
        
        from genie_assistant import GenieAssistant
        print("✅ GenieAssistant importado com sucesso")
        
        # Testar instanciação
        engine = IngestionEngine("test_schema", "test_table")
        print("✅ IngestionEngine instanciado com sucesso")
        
        workflow = WorkflowManager("test_schema", "test_table")
        print("✅ WorkflowManager instanciado com sucesso")
        
        genie = GenieAssistant("test_schema", "test_table")
        print("✅ GenieAssistant instanciado com sucesso")
        
        print("\n🎉 Todos os testes passaram! Estrutura está funcionando.")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def test_cli_help():
    """Testa se a CLI funciona"""
    print("\n🧪 Testando CLI...")
    
    try:
        import cli
        print("✅ Módulo CLI importado com sucesso")
        print("💡 Execute 'python cli.py --help' para ver as opções")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste CLI: {str(e)}")
        return False

def show_structure():
    """Mostra a estrutura simplificada"""
    print("\n📁 ESTRUTURA SIMPLIFICADA DO DINO SDK:")
    print("=" * 50)
    print("dino_sdk/")
    print("├── cli.py                 # 🖥️  Interface de linha de comando")
    print("├── ingestion_engine.py    # ⚙️  Motor de ingestão híbrido")
    print("├── workflow_manager.py    # 🔧 Gerador de workflows")
    print("├── genie_assistant.py     # 🧞 Integração com Genie")
    print("├── __init__.py           # 📦 Módulo principal")
    print("├── requirements.txt      # 📋 Dependências")
    print("├── setup.py             # ⚙️  Configuração de instalação")
    print("├── README.md            # 📖 Documentação")
    print("└── tests/               # 🧪 Testes unitários")
    print()
    print("✨ CARACTERÍSTICAS:")
    print("   • Estrutura plana e simples")
    print("   • Sem duplicação de diretórios")
    print("   • Módulos independentes")
    print("   • Fácil manutenção")

def main():
    """Função principal"""
    print("🦕 DINO SDK - TESTE DA ESTRUTURA SIMPLIFICADA")
    print("=" * 60)
    
    # Executar testes
    success = test_imports() and test_cli_help()
    
    # Mostrar estrutura
    show_structure()
    
    # Resumo
    print("\n📋 RESUMO:")
    if success:
        print("✅ Estrutura simplificada funcionando perfeitamente!")
        print("🚀 Pronto para uso com: python cli.py --help")
    else:
        print("❌ Alguns problemas encontrados")
        print("💡 Verifique as dependências")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. pip install -e .           # Instalar em modo desenvolvimento")
    print("   2. dino-ingest --help          # Testar CLI")
    print("   3. Configurar Databricks       # Preparar ambiente")

if __name__ == "__main__":
    main()
