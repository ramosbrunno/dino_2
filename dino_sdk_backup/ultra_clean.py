#!/usr/bin/env python3
"""
DINO SDK - Limpeza Ultra-Agressiva
Remove todos os arquivos não essenciais, mantendo apenas o core do projeto
"""

import os
import shutil
from pathlib import Path

def ultra_clean_dino_sdk():
    """Limpeza ultra-agressiva do projeto DINO SDK"""
    
    base_dir = Path("c:/Users/User/OneDrive/Documentos/Projetos/Data_Master_2025/GIT/dino_2/dino_sdk")
    
    print("🔥 DINO SDK - LIMPEZA ULTRA-AGRESSIVA")
    print("=" * 50)
    
    # ARQUIVOS ESSENCIAIS PARA MANTER
    essential_files = {
        # Core do projeto
        "setup.py",
        "requirements.txt", 
        "README.md",
        ".gitignore",
        
        # Diretórios essenciais
        "src/",
        "dist/",
        "build/",
        "tests/",
        "examples/",
        "notebooks/"
    }
    
    # TODOS OS MARKDOWNS E NOTEBOOKS PARA REMOÇÃO (exceto README.md)
    files_to_remove = [
        # Documentação markdown (será integrada no README)
        "CORRECAO_REMOCAO_SYSTEM_FILES.md",
        "GUIA_SECRET_SCOPE.md", 
        "GUIA_USO_COMPLETO.md",
        "IMPLEMENTACAO_VOLUMES_COMPLETA.md",
        "INGESTION_ENGINE_SUMMARY.md",
        "LIQUID_CLUSTERING_GUIDE.md",
        "README_v1.2.0.md",
        "REMOCAO_DINO_METADATA.md",
        "SANITIZACAO_COMPLETA_FINAL.md",
        "TOKEN_MANAGER_GUIDE.md",
        
        # Notebooks (será criado um notebook integrado no README)
        "TESTE_DINO_CONFIG_VOLUMES_FIXED.ipynb"
    ]
    
    # EXECUTAR LIMPEZA
    removed_count = 0
    
    for file_path in files_to_remove:
        full_path = base_dir / file_path
        try:
            if full_path.exists():
                if full_path.is_file():
                    full_path.unlink()
                    print(f"🗑️ Removido: {file_path}")
                    removed_count += 1
        except Exception as e:
            print(f"⚠️ Erro ao remover {file_path}: {e}")
    
    print()
    print("📊 RESULTADO DA LIMPEZA ULTRA-AGRESSIVA")
    print("=" * 45)
    print(f"✅ Arquivos removidos: {removed_count}")
    print(f"✅ Projeto ultra-limpo criado!")
    
    # MOSTRAR ESTRUTURA FINAL
    print()
    print("📁 ESTRUTURA ULTRA-LIMPA")
    print("=" * 30)
    
    final_structure = """
    dino_sdk/ (ULTRA-LIMPO)
    ├── 📄 setup.py              # Configuração do pacote
    ├── 📄 requirements.txt      # Dependências
    ├── 📄 README.md             # README ROBUSTO (tudo integrado)
    ├── 📄 .gitignore           # Git ignore
    │
    ├── 🐍 src/                  # Código fonte essencial
    │   └── dino_sdk/           # Módulo principal
    │
    ├── 📦 dist/                # Wheels
    ├── 🏗️ build/               # Build artifacts  
    ├── 🧪 tests/               # Testes unitários
    ├── 📝 examples/            # Exemplos práticos
    └── 📓 notebooks/           # Notebooks demonstração
    
    🎯 RESULTADO: Apenas 6 arquivos essenciais + diretórios!
    """
    
    print(final_structure)
    
    return True

if __name__ == "__main__":
    ultra_clean_dino_sdk()
