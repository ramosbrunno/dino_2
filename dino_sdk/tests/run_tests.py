"""
Arquivo de configuração para execução de todos os testes
"""

import unittest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importar todos os módulos de teste
from test_ingestion_engine import TestIngestionEngine
from test_workflow_manager import TestWorkflowManager
from test_genie_assistant import TestGenieAssistant
from test_integration import TestSDKIntegration


def create_test_suite():
    """Cria uma suite com todos os testes"""
    suite = unittest.TestSuite()
    
    # Adicionar testes de cada módulo
    suite.addTest(unittest.makeSuite(TestIngestionEngine))
    suite.addTest(unittest.makeSuite(TestWorkflowManager))
    suite.addTest(unittest.makeSuite(TestGenieAssistant))
    suite.addTest(unittest.makeSuite(TestSDKIntegration))
    
    return suite


def run_all_tests():
    """Executa todos os testes do SDK"""
    print("🧪 Executando todos os testes do Dino SDK...")
    print("=" * 60)
    
    # Criar suite de testes
    suite = create_test_suite()
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"⚠️  Erros: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FALHAS:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️  ERROS:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("\n💡 Alguns testes falharam. Verifique a implementação.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
