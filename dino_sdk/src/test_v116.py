"""
🧪 Teste Rápido v1.1.6 - Detecção Melhorada de Databricks
"""

# Teste da nova versão com detecção melhorada
from keyvault_config_v116 import quick_setup, extract_databricks_context

def test_v116():
    """
    Testa a versão 1.1.6 com detecção melhorada
    """
    print("🧪 TESTE DINO SDK v1.1.6")
    print("=" * 40)
    
    try:
        # Teste 1: Tentar setup normal
        print("\n1️⃣ Tentando setup normal...")
        try:
            config = quick_setup()
            print("✅ Setup normal funcionou!")
            return config
        except Exception as e:
            print(f"❌ Setup normal falhou: {e}")
            
            # Teste 2: Tentar com force=True
            print("\n2️⃣ Tentando com force=True...")
            try:
                config = quick_setup(force=True)
                print("✅ Setup forçado funcionou!")
                return config
            except Exception as e:
                print(f"❌ Setup forçado também falhou: {e}")
                
                # Teste 3: Apenas extrair contexto
                print("\n3️⃣ Tentando apenas extrair contexto...")
                try:
                    context = extract_databricks_context(force=True)
                    print(f"✅ Contexto extraído: {context.get('extraction_method', 'unknown')}")
                    return context
                except Exception as e:
                    print(f"❌ Extração de contexto falhou: {e}")
                    return None
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None

if __name__ == "__main__":
    result = test_v116()
    
    if result:
        print("\n🎉 TESTE BEM-SUCEDIDO!")
        print("✅ v1.1.6 está funcionando")
    else:
        print("\n❌ TESTE FALHOU")
        print("💡 Execute no Databricks notebook para melhor resultado")
