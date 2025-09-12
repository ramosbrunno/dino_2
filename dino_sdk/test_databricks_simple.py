# 🦕 DINO SDK v1.2.0 - Test Rápido de Importação
# Para Databricks: Copie este código para uma célula e execute

# Test de importação básico
print("=== DINO SDK v1.2.0 - Import Test ===")
try:
    from dino_sdk import (
        IngestionEngine, 
        SchemaManager, 
        DataReader, 
        DataSaver, 
        ConfigValidator
    )
    import dino_sdk
    
    print("✅ SUCESSO! Todas as classes importadas:")
    print(f"  📦 DINO SDK version: {dino_sdk.__version__}")
    print(f"  🔧 IngestionEngine: {IngestionEngine}")
    print(f"  📋 SchemaManager: {SchemaManager}")  
    print(f"  📖 DataReader: {DataReader}")
    print(f"  💾 DataSaver: {DataSaver}")
    print(f"  ✅ ConfigValidator: {ConfigValidator}")
    
    print("\n=== Teste de Funcionalidade ===")
    validator = ConfigValidator()
    print("✅ ConfigValidator instantiated successfully")
    print(f"Available methods: {[m for m in dir(validator) if not m.startswith('_')]}")
    
    print("\n🎉 DINO SDK v1.2.0 está funcionando perfeitamente!")
    print("Ready para ingestão de dados com Unity Catalog e Liquid Clustering! 🚀")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("\nVerifique se o wheel foi instalado corretamente:")
    print("pip install /dbfs/wheels/dino_sdk-1.2.0-py3-none-any.whl --force-reinstall")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
