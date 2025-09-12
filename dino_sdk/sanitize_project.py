#!/usr/bin/env python3
"""
DINO SDK - Script de Sanitização e Equalização
Organiza, limpa e estrutura o projeto DINO SDK
"""

import os
import shutil
from pathlib import Path

def sanitize_dino_sdk():
    """Sanitiza e equaliza o projeto DINO SDK"""
    
    base_dir = Path("c:/Users/User/OneDrive/Documentos/Projetos/Data_Master_2025/GIT/dino_2/dino_sdk")
    
    print("🧹 DINO SDK - Sanitização e Equalização")
    print("=" * 50)
    
    # 1. ARQUIVOS ESSENCIAIS (manter)
    essential_files = {
        # Arquivos de configuração
        "setup.py",
        "requirements.txt", 
        "README.md",
        ".gitignore",
        
        # Documentação final
        "README_v1.2.0.md",
        "IMPLEMENTACAO_VOLUMES_COMPLETA.md",
        "CORRECAO_REMOCAO_SYSTEM_FILES.md",
        "INGESTION_ENGINE_SUMMARY.md",
        "LIQUID_CLUSTERING_GUIDE.md",
        "REMOCAO_DINO_METADATA.md",
        
        # Guias importantes
        "GUIA_USO_COMPLETO.md",
        "GUIA_SECRET_SCOPE.md",
        "TOKEN_MANAGER_GUIDE.md",
        
        # Notebook de teste final
        "TESTE_DINO_CONFIG_VOLUMES_FIXED.ipynb",
        
        # Diretórios essenciais
        "src/",
        "dist/",
        "build/",
        "examples/",
        "notebooks/",
        "tests/"
    }
    
    # 2. ARQUIVOS PARA REMOÇÃO (temporários, duplicados, obsoletos)
    files_to_remove = [
        # Arquivos de análise e debug temporários
        "ANALISE_PROBLEMAS_CLI_SPARK_CONNECT.md",
        "ANALISE_SPARK_CONNECT_URL_ERROR.md",
        "AUTOLOADER_BATCH_FIXES.md",
        "AUTOLOADER_FINAL_SOLUTION.md",
        "CELEBRACAO_SUCESSO_TOTAL.md",
        "CORRECAO_DATABRICKS_v1.2.0.md",
        "CORRECAO_FINAL_TODOS_COMANDOS_CLI.md", 
        "CORRECAO_SPARK_CONNECT.md",
        "CORRECAO_V120.md",
        "DECISAO_TECNICA_METODO_ALTERNATIVO.md",
        "EXECUTION_MODE_FIX.md",
        "NOTEBOOK_BATCH_SOLUTION.md",
        "NOTEBOOK_CORRECTIONS_SUMMARY.md",
        "PROJETO_LIMPO_v113_RESUMO.md",
        "ROBUST_DETECTION_v112_RESUMO.md",
        "SOLUCAO_FINAL_README.md",
        "SOLUCAO_FINAL_SparkSessionManager.md",
        "STATUS_FINAL_SETEMBRO_2025.md",
        "TYPE_RUN_FINAL_FIX.md",
        "VERSAO_COMPATIVEL_FINAL.md",
        
        # CHANGELOGs antigos
        "CHANGELOG_v116.md",
        "RELEASE_NOTES_v1.1.4.md", 
        "RELEASE_NOTES_v1.1.5.md",
        "RELATORIO_REFATORACAO_v1.2.0.md",
        
        # Scripts temporários e correções
        "cleanup_project.py",
        "DATABRICKS_CONFIGVALIDATOR_FIX_COMPLETE.py",
        "DATABRICKS_FIX.txt",
        "DATABRICKS_NOTEBOOK_COMPLETE.py",
        "exemplo_uso_databricks.py",
        "fix_databricks_configvalidator.py",
        "NOTEBOOK_FIXES.py",
        "notebook_import_fix.py", 
        "notebook_working_example.py",
        
        # Notebooks de teste antigos/duplicados
        "teste_cli_final_v120.ipynb",
        "teste_correcao_v120.ipynb", 
        "teste_databricks_v120.ipynb",
        "TESTE_DINO_CONFIG_VOLUMES.ipynb",  # Versão com erro
        "test_ingestion_engine.ipynb",
        "Test_Dino_SDK_v112_FINAL.ipynb",
        
        # Scripts de teste temporários
        "test_databricks_complete.py",
        "test_databricks_simple.py",
        "test_imports_v120.py",
        "test_wheel_installation.py",
        
        # Arquivos src duplicados/obsoletos
        "src/config_cli_old.py",
        "src/databricks_sdk_auth_v114.py",
        "src/dbutils_detection_v113.py", 
        "src/get_notebook_context_v114.py",
        "src/simple_databricks_test.py"
    ]
    
    # 3. EXECUTAR LIMPEZA
    removed_count = 0
    
    for file_path in files_to_remove:
        full_path = base_dir / file_path
        try:
            if full_path.exists():
                if full_path.is_file():
                    full_path.unlink()
                    print(f"🗑️ Removido arquivo: {file_path}")
                    removed_count += 1
                elif full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"🗑️ Removido diretório: {file_path}")
                    removed_count += 1
        except Exception as e:
            print(f"⚠️ Erro ao remover {file_path}: {e}")
    
    # 4. LIMPAR CACHE
    cache_dirs = [
        "src/__pycache__",
        "src/dino_sdk/__pycache__",
        "src/dino_sdk.egg-info"
    ]
    
    for cache_dir in cache_dirs:
        cache_path = base_dir / cache_dir
        try:
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"🧹 Limpo cache: {cache_dir}")
                removed_count += 1
        except Exception as e:
            print(f"⚠️ Erro ao limpar cache {cache_dir}: {e}")
    
    print()
    print("📊 RESUMO DA SANITIZAÇÃO")
    print("=" * 30)
    print(f"✅ Arquivos/diretórios removidos: {removed_count}")
    print(f"✅ Projeto sanitizado e equalizado!")
    print()
    
    # 5. MOSTRAR ESTRUTURA FINAL
    print("📁 ESTRUTURA FINAL DO PROJETO")
    print("=" * 35)
    
    essential_structure = """
    dino_sdk/
    ├── 📄 setup.py
    ├── 📄 requirements.txt
    ├── 📄 README.md
    ├── 📄 .gitignore
    │
    ├── 📚 DOCUMENTAÇÃO/
    │   ├── 📄 README_v1.2.0.md
    │   ├── 📄 IMPLEMENTACAO_VOLUMES_COMPLETA.md
    │   ├── 📄 CORRECAO_REMOCAO_SYSTEM_FILES.md
    │   ├── 📄 INGESTION_ENGINE_SUMMARY.md
    │   ├── 📄 LIQUID_CLUSTERING_GUIDE.md
    │   ├── 📄 REMOCAO_DINO_METADATA.md
    │   ├── 📄 GUIA_USO_COMPLETO.md
    │   ├── 📄 GUIA_SECRET_SCOPE.md
    │   └── 📄 TOKEN_MANAGER_GUIDE.md
    │
    ├── 🐍 CÓDIGO FONTE/
    │   └── src/
    │       ├── dino_sdk/
    │       │   ├── __init__.py
    │       │   ├── cli.py
    │       │   ├── ingestion_engine.py
    │       │   ├── schema_manager.py
    │       │   ├── workflow_manager.py
    │       │   └── genie_assistant.py
    │       ├── config_cli.py
    │       ├── config_manager.py
    │       └── [outros arquivos essenciais]
    │
    ├── 🧪 TESTES/
    │   ├── 📓 TESTE_DINO_CONFIG_VOLUMES_FIXED.ipynb
    │   └── tests/
    │
    ├── 📦 DISTRIBUIÇÃO/
    │   ├── dist/ (wheels)
    │   └── build/
    │
    ├── 📝 EXEMPLOS/
    │   ├── examples/
    │   └── notebooks/
    │
    └── 🎯 RESULTADO: Projeto limpo, organizado e pronto para produção!
    """
    
    print(essential_structure)
    
    return True

if __name__ == "__main__":
    sanitize_dino_sdk()
