#!/usr/bin/env python3
"""
Test Runner para Dino ARC
Executa todos os testes do projeto
"""

import sys
import os
import unittest
from pathlib import Path

# Adicionar src ao path para imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

def run_all_tests():
    """Executa todos os testes do projeto"""
    
    # Descobrir todos os testes
    loader = unittest.TestLoader()
    start_dir = str(current_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resultado
    if result.wasSuccessful():
        print(f"\n✅ Todos os {result.testsRun} testes passaram!")
        return 0
    else:
        print(f"\n❌ {len(result.failures)} testes falharam, {len(result.errors)} erros")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())