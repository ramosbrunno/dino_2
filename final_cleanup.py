#!/usr/bin/env python3
"""
🧹 DINO SDK - Limpeza Final de Arquivos de Desenvolvimento

Remove arquivos de documentação de desenvolvimento, troubleshooting e correções
que não são mais necessários no projeto final.
"""

import os
import shutil
from pathlib import Path

def clean_development_files():
    """Remove arquivos de desenvolvimento não essenciais"""
    
    print("🧹 DINO SDK - Limpeza Final de Arquivos de Desenvolvimento")
    print("=" * 60)
    
    # Diretório base (raiz do repositório)
    base_dir = Path(__file__).parent
    
    # Arquivos de desenvolvimento para remover
    dev_files_to_remove = [
        "AUTOLOADER_SCHEMA_LOCATION_FIX.md",
        "CLASS_METHOD_FIXES.md", 
        "DINO_SDK_CLI_SIMPLIFIED_FINAL.md",
        "DINO_SDK_SCHEMA_MANAGER_REPORT.md",
        "DINO_SDK_V1.2.0_TRANSFORMACAO_FINAL.md",
        "DINO_SDK_V1.2.0_FINAL_REPORT.md",
        "LIQUID_CLUSTERING_CONFIG_FIX.md",
        "SOLUCAO_BATCH_SAVE_ERROR.md",
        "SOLUCAO_CLUSTERING_COLUMN_ERROR.md", 
        "SOLUCAO_SCHEMA_COMPATIBILITY_ERROR.md",
        "SOLUCAO_TEMP_TABLE_ERROR.md",
        "test_ingestion_engine_fixed.ipynb"
    ]
    
    print("📋 Arquivos marcados para remoção:")
    for file_name in dev_files_to_remove:
        print(f"   • {file_name}")
    
    # Contadores
    removed_count = 0
    not_found_count = 0
    total_size_removed = 0
    
    print(f"\n🔍 Verificando e removendo arquivos...")
    
    # Remover cada arquivo
    for file_name in dev_files_to_remove:
        file_path = base_dir / file_name
        
        if file_path.exists():
            try:
                # Obter tamanho antes de remover
                file_size = file_path.stat().st_size
                total_size_removed += file_size
                
                # Remover arquivo
                file_path.unlink()
                
                print(f"   ✅ {file_name} removido ({file_size:,} bytes)")
                removed_count += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao remover {file_name}: {e}")
        else:
            print(f"   ℹ️ {file_name} não encontrado (já removido?)")
            not_found_count += 1
    
    # Resumo da limpeza
    print(f"\n📊 RESUMO DA LIMPEZA")
    print("=" * 25)
    print(f"✅ Arquivos removidos: {removed_count}")
    print(f"ℹ️ Não encontrados: {not_found_count}")
    print(f"📦 Espaço liberado: {total_size_removed:,} bytes ({total_size_removed/1024:.1f} KB)")
    
    # Verificar estrutura final
    print(f"\n📁 ESTRUTURA FINAL DO REPOSITÓRIO")
    print("=" * 35)
    
    # Listar arquivos na raiz
    root_files = []
    root_dirs = []
    
    for item in base_dir.iterdir():
        if item.name.startswith('.'):
            continue  # Ignorar arquivos ocultos
            
        if item.is_file():
            root_files.append(item.name)
        elif item.is_dir():
            root_dirs.append(item.name)
    
    print("📄 Arquivos na raiz:")
    for file in sorted(root_files):
        print(f"   • {file}")
    
    print(f"\n📂 Diretórios:")
    for dir in sorted(root_dirs):
        print(f"   • {dir}/")
    
    print(f"\n📈 Total de itens na raiz: {len(root_files) + len(root_dirs)}")
    
    # Verificar se a pasta dino_sdk está limpa
    dino_sdk_path = base_dir / "dino_sdk"
    if dino_sdk_path.exists():
        print(f"\n🦕 Estrutura da pasta dino_sdk:")
        dino_items = list(dino_sdk_path.iterdir())
        for item in sorted(dino_items):
            if item.is_dir():
                print(f"   📂 {item.name}/")
            else:
                print(f"   📄 {item.name}")
        
        print(f"   Total: {len(dino_items)} itens")
    
    if removed_count > 0:
        print(f"\n🎉 Limpeza concluída! {removed_count} arquivos de desenvolvimento removidos.")
        print("🚀 Projeto está agora em sua forma mais limpa e profissional!")
    else:
        print(f"\n✨ Projeto já estava limpo! Nenhum arquivo de desenvolvimento encontrado.")
    
    return removed_count

def verify_essential_files():
    """Verifica se todos os arquivos essenciais ainda estão presentes"""
    
    print(f"\n✅ VERIFICAÇÃO DE ARQUIVOS ESSENCIAIS")
    print("=" * 40)
    
    base_dir = Path(__file__).parent
    dino_sdk_path = base_dir / "dino_sdk"
    
    essential_files = {
        "README.md": "Documentação principal",
        "dino_sdk/setup.py": "Configuração do pacote",
        "dino_sdk/requirements.txt": "Dependências",
        "dino_sdk/src/dino_sdk/__init__.py": "Módulo principal",
        "dino_sdk/src/dino_sdk/ingestion_engine.py": "Motor de ingestão",
        "dino_sdk/src/dino_sdk/schema_manager.py": "Gerenciador de schemas",
        "dino_sdk/dist/dino_sdk-1.2.0-py3-none-any.whl": "Wheel de distribuição"
    }
    
    all_present = True
    
    for file_path, description in essential_files.items():
        full_path = base_dir / file_path
        
        if full_path.exists():
            if full_path.is_file():
                size = full_path.stat().st_size
                print(f"   ✅ {file_path} ({size:,} bytes) - {description}")
            else:
                print(f"   ✅ {file_path}/ - {description}")
        else:
            print(f"   ❌ {file_path} - {description} (FALTANDO!)")
            all_present = False
    
    if all_present:
        print(f"\n🎉 Todos os arquivos essenciais estão presentes!")
    else:
        print(f"\n⚠️ Alguns arquivos essenciais estão faltando!")
    
    return all_present

if __name__ == "__main__":
    """Execução da limpeza"""
    
    try:
        print("🦕 DINO SDK - Limpeza Final")
        print("Este script remove arquivos de desenvolvimento não essenciais")
        print("Arquivos essenciais do projeto serão preservados")
        
        # Executar limpeza
        removed_count = clean_development_files()
        
        # Verificar arquivos essenciais
        all_essential_present = verify_essential_files()
        
        # Status final
        if all_essential_present:
            print(f"\n✨ LIMPEZA CONCLUÍDA COM SUCESSO!")
            print(f"🦕 DINO SDK está em sua forma mais limpa e profissional!")
            
            if removed_count > 0:
                print(f"📦 {removed_count} arquivos de desenvolvimento removidos")
            print(f"🚀 Projeto pronto para uso e distribuição!")
        else:
            print(f"\n⚠️ Limpeza concluída mas alguns arquivos essenciais estão faltando")
            print(f"Verifique a integridade do projeto antes de usar")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        import traceback
        traceback.print_exc()
