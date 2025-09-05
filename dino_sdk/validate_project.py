#!/usr/bin/env python3
"""
🦕 DINO SDK v1.2.0 - Validação Final do Projeto

Script para validar que toda a estrutura do projeto está correta e pronta para uso.
"""

import os
import sys
from pathlib import Path

def validate_project_structure():
    """Valida a estrutura do projeto DINO SDK"""
    
    print("🦕 DINO SDK v1.2.0 - Validação Final")
    print("=" * 45)
    
    # Estrutura esperada
    expected_structure = {
        "files": [
            "setup.py",
            "requirements.txt", 
            "README.md",
            ".gitignore"
        ],
        "directories": [
            "src",
            "src/dino_sdk",
            "tests",
            "examples", 
            "notebooks",
            "dist",
            "build"
        ],
        "core_modules": [
            "src/dino_sdk/__init__.py",
            "src/dino_sdk/cli.py",
            "src/dino_sdk/ingestion_engine.py",
            "src/dino_sdk/schema_manager.py",
            "src/dino_sdk/workflow_manager.py",
            "src/dino_sdk/genie_assistant.py"
        ],
        "example_files": [
            "examples/exemplo_completo.py"
        ],
        "notebooks": [
            "notebooks/DINO_SDK_Demo_Completa.ipynb"
        ],
        "dist_files": [
            "dist/dino_sdk-1.2.0-py3-none-any.whl"
        ]
    }
    
    # Validar cada categoria
    project_root = Path.cwd()
    validation_results = {}
    
    print(f"📁 Projeto: {project_root.name}")
    print(f"📍 Caminho: {project_root}")
    
    # Validar arquivos essenciais
    print(f"\n📄 Validando arquivos essenciais...")
    missing_files = []
    for file_path in expected_structure["files"]:
        if (project_root / file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    validation_results["files"] = len(missing_files) == 0
    
    # Validar diretórios
    print(f"\n📂 Validando diretórios...")
    missing_dirs = []
    for dir_path in expected_structure["directories"]:
        if (project_root / dir_path).exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    validation_results["directories"] = len(missing_dirs) == 0
    
    # Validar módulos principais
    print(f"\n🐍 Validando módulos principais...")
    missing_modules = []
    for module_path in expected_structure["core_modules"]:
        if (project_root / module_path).exists():
            print(f"   ✅ {module_path}")
        else:
            print(f"   ❌ {module_path}")
            missing_modules.append(module_path)
    
    validation_results["core_modules"] = len(missing_modules) == 0
    
    # Validar exemplos
    print(f"\n📝 Validando exemplos...")
    missing_examples = []
    for example_path in expected_structure["example_files"]:
        if (project_root / example_path).exists():
            print(f"   ✅ {example_path}")
        else:
            print(f"   ❌ {example_path}")
            missing_examples.append(example_path)
    
    validation_results["examples"] = len(missing_examples) == 0
    
    # Validar notebooks
    print(f"\n📓 Validando notebooks...")
    missing_notebooks = []
    for notebook_path in expected_structure["notebooks"]:
        if (project_root / notebook_path).exists():
            print(f"   ✅ {notebook_path}")
        else:
            print(f"   ❌ {notebook_path}")
            missing_notebooks.append(notebook_path)
    
    validation_results["notebooks"] = len(missing_notebooks) == 0
    
    # Validar wheel de distribuição
    print(f"\n📦 Validando distribuição...")
    missing_dist = []
    for dist_path in expected_structure["dist_files"]:
        if (project_root / dist_path).exists():
            size_mb = (project_root / dist_path).stat().st_size / (1024 * 1024)
            print(f"   ✅ {dist_path} ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ {dist_path}")
            missing_dist.append(dist_path)
    
    validation_results["distribution"] = len(missing_dist) == 0
    
    # Verificar conteúdo do README
    print(f"\n📖 Validando README...")
    readme_path = project_root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        readme_checks = {
            "título": "DINO SDK v1.2.0" in content,
            "instalação": "Instalação" in content or "Installation" in content,
            "uso": "uso" in content.lower() or "usage" in content.lower(),
            "testes": "teste" in content.lower() or "test" in content.lower(),
            "exemplos": "exemplo" in content.lower() or "example" in content.lower()
        }
        
        for check, passed in readme_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            
        validation_results["readme"] = all(readme_checks.values())
    else:
        validation_results["readme"] = False
    
    # Resumo final
    print(f"\n🎯 RESUMO DA VALIDAÇÃO")
    print("=" * 30)
    
    all_passed = True
    for category, passed in validation_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {category.replace('_', ' ').title()}")
        if not passed:
            all_passed = False
    
    print(f"\n{'🎉' if all_passed else '⚠️'} Status geral: {'APROVADO' if all_passed else 'PENDENTE'}")
    
    if all_passed:
        print("\n✨ PROJETO DINO SDK v1.2.0 VALIDADO COM SUCESSO!")
        print("🚀 Pronto para uso e distribuição!")
        print("\n📋 Próximos passos:")
        print("   • Testar instalação em ambiente Databricks")
        print("   • Executar notebook de demonstração")
        print("   • Validar funcionalidades com dados reais")
    else:
        print("\n⚠️ Alguns componentes precisam de atenção")
        print("📋 Verifique os itens marcados com ❌")
    
    return all_passed

def show_project_summary():
    """Mostra resumo do projeto"""
    
    print(f"\n📊 RESUMO DO PROJETO DINO SDK")
    print("=" * 35)
    
    project_info = {
        "🦕 Nome": "DINO SDK v1.2.0",
        "📝 Descrição": "Data Integration & Operations SDK para Databricks Unity Catalog",
        "🎯 Funcionalidades": [
            "AutoLoader integrado",
            "Liquid Clustering",
            "Volumes gerenciados", 
            "Schema evolution",
            "CLI integrada",
            "Notebooks de demo"
        ],
        "📦 Componentes": [
            "IngestionEngine - Motor de ingestão",
            "SchemaManager - Gerenciamento de schemas/volumes",
            "WorkflowManager - Orquestração",
            "CLI - Interface de linha de comando"
        ],
        "🧪 Testes": [
            "Testes unitários (pytest)",
            "Notebook de demonstração completa",
            "Exemplos práticos de uso",
            "Validação de funcionalidades"
        ]
    }
    
    for key, value in project_info.items():
        print(f"\n{key}: ", end="")
        if isinstance(value, list):
            print("")
            for item in value:
                print(f"   • {item}")
        else:
            print(value)

if __name__ == "__main__":
    """Execução da validação"""
    
    try:
        # Validar estrutura
        validation_passed = validate_project_structure()
        
        # Mostrar resumo
        show_project_summary()
        
        # Status de saída
        if validation_passed:
            print(f"\n🎉 Validação concluída com sucesso!")
            sys.exit(0)
        else:
            print(f"\n⚠️ Validação encontrou problemas")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        sys.exit(1)
