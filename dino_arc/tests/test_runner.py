"""
Suite de testes completa para o projeto Dino ARC
"""
import unittest
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importar todos os módulos de teste com imports relativos
from .test_azure_auth import TestAzureAuth
from .test_terraform_executor import TestTerraformExecutor
from .test_databricks_configurator import TestDatabricksConfigurator
from .test_cli_integration import TestCLIIntegration, TestCLIArguments
from .test_terraform_validation import TestTerraformFiles, TestTerraformConfiguration


def create_test_suite():
    """
    Cria a suite completa de testes
    """
    suite = unittest.TestSuite()
    
    # Testes unitários dos módulos SDK
    suite.addTest(unittest.makeSuite(TestAzureAuth))
    suite.addTest(unittest.makeSuite(TestTerraformExecutor))
    
    # Testes do configurador Databricks
    suite.addTest(unittest.makeSuite(TestDatabricksConfigurator))
    
    # Testes de integração da CLI
    suite.addTest(unittest.makeSuite(TestCLIIntegration))
    suite.addTest(unittest.makeSuite(TestCLIArguments))
    
    # Testes de validação do Terraform
    suite.addTest(unittest.makeSuite(TestTerraformFiles))
    suite.addTest(unittest.makeSuite(TestTerraformConfiguration))
    
    return suite


def run_tests():
    """
    Executa todos os testes
    """
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test_module(module_name):
    """
    Executa testes de um módulo específico
    """
    module_mapping = {
        'azure_auth': TestAzureAuth,
        'terraform_executor': TestTerraformExecutor,
        'databricks_configurator': TestDatabricksConfigurator,
        'cli_integration': TestCLIIntegration,
        'cli_arguments': TestCLIArguments,
        'terraform_files': TestTerraformFiles,
        'terraform_config': TestTerraformConfiguration
    }
    
    if module_name not in module_mapping:
        print(f"Módulo '{module_name}' não encontrado.")
        print(f"Módulos disponíveis: {', '.join(module_mapping.keys())}")
        return False
    
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(module_mapping[module_name]))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Executar testes do Dino ARC')
    parser.add_argument('--module', '-m', 
                       help='Executar testes de um módulo específico')
    parser.add_argument('--list', '-l', action='store_true',
                       help='Listar módulos de teste disponíveis')
    
    args = parser.parse_args()
    
    if args.list:
        modules = [
            'azure_auth',
            'terraform_executor', 
            'databricks_configurator',
            'cli_integration',
            'cli_arguments',
            'terraform_files',
            'terraform_config'
        ]
        print("Módulos de teste disponíveis:")
        for module in modules:
            print(f"  - {module}")
        sys.exit(0)
    
    if args.module:
        success = run_specific_test_module(args.module)
    else:
        print("🧪 Executando suite completa de testes do Dino ARC...")
        print("=" * 60)
        success = run_tests()
    
    if success:
        print("\n✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam!")
        sys.exit(1)
