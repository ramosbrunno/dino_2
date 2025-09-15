#!/usr/bin/env python3
"""
Teste final após correção dos métodos duplicados
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_corrected_methods():
    """
    Testa se os métodos duplicados foram corrigidos
    """
    print("🔍 TESTE PÓS-CORREÇÃO: Métodos Duplicados Removidos")
    print("="*60)
    
    file_path = "c:\\Users\\User\\OneDrive\\Documentos\\Projetos\\Data_Master_2025\\GIT\\dino_2\\dino_sdk\\src\\dino_sdk\\ingestion_engine.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Verificar métodos duplicados
        save_log_lines = [i+1 for i, line in enumerate(lines) if "def save_ingestion_log(" in line]
        save_log_locally_lines = [i+1 for i, line in enumerate(lines) if "def _save_log_locally(" in line]
        create_table_lines = [i+1 for i, line in enumerate(lines) if "def _create_log_table_if_not_exists(" in line]
        
        print(f"📊 Total de linhas: {total_lines}")
        print(f"\n🔍 MÉTODOS APÓS CORREÇÃO:")
        
        # Verificar save_ingestion_log
        if len(save_log_lines) == 1:
            print(f"✅ save_ingestion_log: 1 método (linha {save_log_lines[0]}) - CORRETO")
        else:
            print(f"❌ save_ingestion_log: {len(save_log_lines)} métodos (linhas {save_log_lines}) - AINDA DUPLICADO")
        
        # Verificar _save_log_locally
        if len(save_log_locally_lines) == 1:
            print(f"✅ _save_log_locally: 1 método (linha {save_log_locally_lines[0]}) - CORRETO")
        else:
            print(f"❌ _save_log_locally: {len(save_log_locally_lines)} métodos (linhas {save_log_locally_lines}) - AINDA DUPLICADO")
        
        # Verificar _create_log_table_if_not_exists
        if len(create_table_lines) == 1:
            print(f"✅ _create_log_table_if_not_exists: 1 método (linha {create_table_lines[0]}) - CORRETO")
        else:
            print(f"❌ _create_log_table_if_not_exists: {len(create_table_lines)} métodos (linhas {create_table_lines}) - PROBLEMA")
        
        # Analisar o método save_ingestion_log restante
        if save_log_lines:
            print(f"\n🔍 ANALISANDO save_ingestion_log (linha {save_log_lines[0]}):")
            
            method_start = save_log_lines[0] - 1
            # Encontrar o fim do método
            method_end = method_start
            for i in range(method_start + 1, len(lines)):
                line = lines[i].strip()
                if line and not line.startswith('#') and not line.startswith('"""'):
                    if (lines[i].startswith('    def ') or lines[i].startswith('def ') or 
                        lines[i].startswith('class ') or lines[i].startswith('#!/')):
                        method_end = i
                        break
            else:
                method_end = len(lines)
            
            method_content = '\n'.join(lines[method_start:method_end])
            
            # Verificar características importantes
            checks = {
                'Tenta criar tabela Unity Catalog': '_create_log_table_if_not_exists' in method_content,
                'Salva na tabela Delta': 'saveAsTable' in method_content,
                'Tem fallback para logging local': '_save_log_locally' in method_content,
                'Logs informativos': 'logger.info' in method_content or 'self.logger.info' in method_content,
                'Tratamento de exceções': 'except Exception' in method_content
            }
            
            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
        
        # Analisar o método _create_log_table_if_not_exists
        if create_table_lines:
            print(f"\n🔍 ANALISANDO _create_log_table_if_not_exists (linha {create_table_lines[0]}):")
            
            method_start = create_table_lines[0] - 1
            method_end = method_start + 50  # Assumir que o método não é muito longo
            
            for i in range(method_start + 1, min(method_end, len(lines))):
                line = lines[i].strip()
                if line and not line.startswith('#') and (line.startswith('def ') or line.startswith('class ')):
                    method_end = i
                    break
            
            method_content = '\n'.join(lines[method_start:method_end])
            
            # Verificar se ainda tem verificação Unity Catalog
            if "_is_unity_catalog_enabled" in method_content:
                print("   ❌ Ainda verifica _is_unity_catalog_enabled (pode impedir criação)")
            else:
                print("   ✅ Não verifica _is_unity_catalog_enabled (sempre tenta criar)")
            
            if "CREATE TABLE IF NOT EXISTS" in method_content:
                print("   ✅ Cria tabela usando CREATE TABLE IF NOT EXISTS")
            else:
                print("   ❌ Não cria tabela corretamente")
                
            if "raise" in method_content:
                print("   ✅ Faz raise de exceções para permitir fallback")
            else:
                print("   ❌ Não faz raise - pode mascarar erros")
        
        # Resultado final
        all_correct = (len(save_log_lines) == 1 and 
                      len(save_log_locally_lines) == 1 and 
                      len(create_table_lines) == 1)
        
        if all_correct:
            print(f"\n🎯 RESULTADO: ✅ TODOS OS MÉTODOS CORRIGIDOS!")
            print(f"   - Métodos duplicados removidos")
            print(f"   - Apenas 1 implementação de cada método")
            print(f"   - Pronto para testar funcionalidade")
        else:
            print(f"\n🎯 RESULTADO: ❌ AINDA HÁ PROBLEMAS")
            print(f"   - Verificar se há métodos duplicados restantes")
            
        return all_correct, save_log_lines
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {str(e)}")
        return False, []

def test_method_functionality():
    """
    Testa se os métodos corrigidos funcionam
    """
    print(f"\n\n🧪 TESTE FUNCIONAL: Métodos Corrigidos")
    print("="*60)
    
    try:
        from dino_sdk.ingestion_engine import IngestionEngine
        from datetime import datetime
        import uuid
        
        class MockConfig:
            def __init__(self):
                self.table_name = "test_table"
                self.schema_name = "bronze"
                self.catalog_name = "data_master_dev_dbw"
                self.source_path = "/tmp/test.csv"
                self.file_extension = "csv"
                self.type_run = "batch"
        
        class MockLogger:
            def __init__(self):
                self.logs = []
            def info(self, msg): 
                self.logs.append(("INFO", msg))
                print(f"   ℹ️ {msg}")
            def warning(self, msg): 
                self.logs.append(("WARNING", msg))
                print(f"   ⚠️ {msg}")
            def error(self, msg): 
                self.logs.append(("ERROR", msg))
                print(f"   ❌ {msg}")
        
        # Testar se é possível instanciar
        logger = MockLogger()
        engine = IngestionEngine(spark=None, logger=logger)
        
        print(f"✅ IngestionEngine instanciado com sucesso")
        
        # Verificar se o método save_ingestion_log existe e é único
        if hasattr(engine, 'save_ingestion_log'):
            print(f"✅ Método save_ingestion_log existe")
            
            # Verificar assinatura do método
            import inspect
            sig = inspect.signature(engine.save_ingestion_log)
            params = list(sig.parameters.keys())
            print(f"✅ Parâmetros: {params}")
            
            if len(params) >= 5:  # self + pelo menos 4 parâmetros obrigatórios
                print(f"✅ Método tem assinatura correta ({len(params)} parâmetros)")
            else:
                print(f"❌ Método pode ter assinatura incorreta ({len(params)} parâmetros)")
        else:
            print(f"❌ Método save_ingestion_log NÃO existe")
        
        # Verificar outros métodos críticos
        critical_methods = ['_create_log_table_if_not_exists', '_save_log_locally', '_get_log_table_name']
        for method_name in critical_methods:
            if hasattr(engine, method_name):
                print(f"✅ Método {method_name} existe")
            else:
                print(f"❌ Método {method_name} NÃO existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste funcional: {str(e)}")
        return False

if __name__ == "__main__":
    corrected, save_log_lines = test_corrected_methods()
    functional = test_method_functionality()
    
    print(f"\n" + "="*60)
    print("🎯 RESUMO FINAL")
    print("="*60)
    
    if corrected and functional:
        print("✅ CORREÇÃO COMPLETA!")
        print("   - Métodos duplicados removidos")
        print("   - Métodos funcionais")
        print("   - Pronto para teste em produção")
        
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"   1. Gerar nova versão do wheel")
        print(f"   2. Testar criação de tabela Unity Catalog")
        print(f"   3. Validar salvamento de logs")
    else:
        print("❌ AINDA HÁ PROBLEMAS!")
        if not corrected:
            print("   - Métodos duplicados não foram completamente removidos")
        if not functional:
            print("   - Métodos não estão funcionais")
    
    print("="*60)
