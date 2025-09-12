#!/usr/bin/env python3
"""
Script de limpeza do projeto Dino SDK v1.1.3
Remove arquivos não essenciais, mantém apenas o necessário para produção
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Limpa projeto mantendo apenas arquivos essenciais"""
    
    project_root = Path(__file__).parent
    backup_dir = project_root / "backup_cleanup"
    
    print("🧹 LIMPEZA DO PROJETO DINO SDK v1.1.3")
    print("=" * 50)
    
    # Criar diretório de backup
    backup_dir.mkdir(exist_ok=True)
    print(f"📁 Backup criado em: {backup_dir}")
    
    # Arquivos e pastas para remover (mover para backup)
    to_remove = [
        # Documentação antiga
        "AUTH_FIX_v108_RESUMO.md",
        "CONTEXT_ENHANCED_v110_RESUMO.md", 
        "CORRECOES_DINO_CONFIG.md",
        "CORRECOES_KEYVAULT.md",
        "ESTRUTURA_REVISADA_FINAL.md",
        "ESTRUTURA_SIMPLIFICADA.md",
        "GUIA_COMPLETO.md",
        "GUIA_CONFIGURACAO_DISTRIBUICAO.md",
        "GUIA_INSTALACAO.md",
        "GUIA_NOTEBOOK_DATABRICKS.md",
        "KEYVAULT_INTEGRATION_COMPLETE.md",
        "NOTEBOOK_FIX_v107_RESUMO.md",
        "NOVA_ESTRUTURA.md",
        "NOVA_ESTRUTURA_YAML.md",
        "PROBLEMAS_CORRIGIDOS.md",
        "README_new.md",
        "RELATORIO_FINAL_DINO_SDK.md",
        "RELATORIO_FINAL_KEYVAULT.md",
        "RESUMO_FINAL_COMPLETO.md",
        "SECRET_SCOPE_v106_RESUMO.md",
        "SIMPLIFIED_v111_RESUMO.md",
        "SOLUCAO_ERRO_CONFIG_NOTEBOOK.md",
        "STATUS_FINAL.md",
        "TOKEN_TEMP_v109_RESUMO.md",
        "ATUALIZACOES_COMANDO.md",
        
        # Scripts de teste antigos
        "check_databricks_env.py",
        "demo_keyvault.py",
        "demo_yaml_structure.py",
        "diagnostic.py",
        "exemplo_completo_atualizado.py",
        "exemplo_keyvault.py",
        "exemplo_logging_completo.py",
        "install_databricks.py",
        "install_incremental.py",
        "simple_context.py",
        "teste_config_programatica.py",
        "test_cli_fixes.py",
        "test_command_structure.py",
        "test_demo.py",
        "test_deps.py",
        "test_direct_context.py",
        "test_keyvault_secret.py",
        "test_minimal_v106.py",
        "test_new_yaml_structure.py",
        "test_secret_scope_v106.py",
        "test_structure.py",
        "test_structure_v106.py",
        "test_yaml_generation.py",
        
        # Notebooks de teste antigos
        "Dino_SDK_v110_Context_Enhanced.ipynb",
        "Fix_SDK_Context_Injection.ipynb",
        "Teste_Dino_Config_Setup_Databricks.ipynb",
        "Test_DBUtils_Direct.ipynb",
        "Test_SDK_v112_Final.ipynb",
        "Test_Simple_DBUtils.ipynb",
        
        # Arquivos de configuração antigos
        "cli.py",  # CLI na raiz (duplicado)
        "setup_new.py",
        "setup.cfg",
        "requirements copy.txt",
        "requirements_minimal.txt",
        "__init__.py",  # Na raiz (duplicado)
        
        # Arquivos temporários
        "dino_job_vendas_db_produtos_20250901_101944.json",
        
        # Pastas de build e cache
        "build",
        "dino_sdk.egg-info",
        "src/__pycache__",
        "demo_volumes",
        
        # Wheels antigos (manter apenas o mais recente)
        "dist/dino_sdk-1.0.9-py3-none-any.whl",
        "dist/dino_sdk-1.1.0-py3-none-any.whl", 
        "dist/dino_sdk-1.1.1-py3-none-any.whl",
        "dist/dino_sdk-1.1.2-py3-none-any.whl",
    ]
    
    # Arquivos essenciais para manter
    essential_files = [
        "README.md",
        "ROBUST_DETECTION_v112_RESUMO.md",  # Documentação da versão atual
        "Test_Dino_SDK_v112_FINAL.ipynb",  # Notebook de teste atual
        "requirements.txt",
        "setup.py",
        "src/",
        "tests/",
        "examples/",
        "dist/dino_sdk-1.1.3-py3-none-any.whl",  # Apenas wheel atual
    ]
    
    moved_count = 0
    
    for item_path in to_remove:
        full_path = project_root / item_path
        
        if full_path.exists():
            try:
                backup_path = backup_dir / item_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                if full_path.is_dir():
                    shutil.move(str(full_path), str(backup_path))
                    print(f"📁 Movido diretório: {item_path}")
                else:
                    shutil.move(str(full_path), str(backup_path))
                    print(f"📄 Movido arquivo: {item_path}")
                    
                moved_count += 1
                
            except Exception as e:
                print(f"❌ Erro ao mover {item_path}: {e}")
        else:
            print(f"⚠️ Não encontrado: {item_path}")
    
    print(f"\n✅ Limpeza concluída!")
    print(f"📊 {moved_count} itens movidos para backup")
    print(f"📁 Backup em: {backup_dir}")
    
    # Mostrar estrutura final
    print(f"\n📂 ESTRUTURA FINAL LIMPA:")
    print("=" * 30)
    for item in sorted(project_root.iterdir()):
        if item.name != "backup_cleanup" and item.name != "cleanup_project.py":
            if item.is_dir():
                print(f"📁 {item.name}/")
                if item.name in ["src", "tests", "examples"]:
                    for subitem in sorted(item.iterdir()):
                        if not subitem.name.startswith('.') and not subitem.name == '__pycache__':
                            print(f"   📄 {subitem.name}")
            else:
                print(f"📄 {item.name}")

if __name__ == "__main__":
    cleanup_project()
