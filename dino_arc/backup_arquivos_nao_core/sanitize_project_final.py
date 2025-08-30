#!/usr/bin/env python3
"""
Script de Sanitização do Projeto Dino ARC
Move arquivos não essenciais para pasta de backup, mantendo apenas o core do projeto
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class DinoArcSanitizer:
    """
    Classe par        # Confirmar ação
        if not auto_confirm:
            print("\n⚠️  Esta operação moverá arquivos para backup.")
            print("   Arquivos core serão mantidos no projeto.")
            response = input("Continuar com a sanitização? (s/N): ").lower().strip()
            
            if response not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada pelo usuário.")
                return False
        else:
            print("\n🚀 Confirmação automática ativada, prosseguindo...")zar o projeto Dino ARC, movendo arquivos não essenciais para backup
    """
    
    def __init__(self, project_root: str):
        """
        Inicializa o sanitizador
        
        Args:
            project_root: Caminho raiz do projeto dino_arc
        """
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "backup_arquivos_nao_core"
        
        # Arquivos e pastas ESSENCIAIS que devem permanecer
        self.core_files = {
            # Arquivos de configuração do projeto
            'setup.py',
            'pyproject.toml', 
            'requirements.txt',
            'MANIFEST.in',
            'README.md',
            'CHANGELOG.md',
            '.gitignore',
            
            # Pastas essenciais
            'src/',
            'terraform/',  # Confirmado pelo usuário que faz parte do projeto
        }
        
        # Padrões de arquivos para mover para backup
        self.backup_patterns = {
            # Arquivos de teste
            'test_*.py',
            'test*.py', 
            'temp_*.py',
            'exemplos_*.py',
            
            # Scripts de automação
            '*.bat',
            '*.ps1', 
            '*.sh',
            
            # Documentação não essencial
            '*README*.md',
            'GUIA_*.md',
            'STATUS_*.md',
            'RELATORIO_*.md',
            'EXEMPLOS_*.md',
            'SANITIZACAO*.md',
            'AUTOMATIZACAO*.md',
            'SIMPLIFICACAO*.md',
            'SOLUCAO*.md',
            'LIMPEZA*.md',
            'PACOTE*.md',
            'TROUBLESHOOTING*.md',
            '*FINAL*.md',
            
            # Arquivos de build/deploy
            'build_*.py',
            'create_*.py',
            'setup_*.py',
            'sanitize_*.py',
            'prepare_*.py',
            
            # Pastas de teste e auxiliares
            'tests/',
            'scripts/',
            'dino_env/',
        }
        
        # Arquivos específicos para backup
        self.specific_backup_files = {
            'dino_arc.py',  # Versão alternativa, mantemos apenas src/cli.py
            'dino_arc_simple.py',
            'temp_dino.py',
            'test_cli.py',
            'test.py',
        }
    
    def create_backup_directory(self) -> bool:
        """
        Cria diretório de backup se não existir
        
        Returns:
            bool: True se criado com sucesso
        """
        try:
            self.backup_dir.mkdir(exist_ok=True)
            print(f"📁 Diretório de backup criado: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar diretório de backup: {e}")
            return False
    
    def identify_files_to_backup(self) -> Tuple[List[Path], List[Path]]:
        """
        Identifica arquivos e pastas para backup
        
        Returns:
            Tuple[List[Path], List[Path]]: (arquivos_para_backup, arquivos_core)
        """
        all_items = list(self.project_root.iterdir())
        files_to_backup = []
        core_files = []
        
        for item in all_items:
            item_name = item.name
            
            # Verificar se é arquivo/pasta core
            if any(item_name.startswith(core.rstrip('/')) for core in self.core_files):
                core_files.append(item)
                continue
            
            # Verificar se deve ir para backup
            should_backup = False
            
            # Verificar arquivos específicos
            if item_name in self.specific_backup_files:
                should_backup = True
            
            # Verificar padrões
            for pattern in self.backup_patterns:
                if pattern.endswith('/'):
                    # É uma pasta
                    if item.is_dir() and item_name == pattern.rstrip('/'):
                        should_backup = True
                        break
                else:
                    # É um arquivo - verificar padrão simples
                    if pattern.startswith('*') and pattern.endswith('*'):
                        # Padrão *texto*
                        text = pattern[1:-1]
                        if text in item_name:
                            should_backup = True
                            break
                    elif pattern.startswith('*'):
                        # Padrão *sufixo
                        suffix = pattern[1:]
                        if item_name.endswith(suffix):
                            should_backup = True
                            break
                    elif pattern.endswith('*'):
                        # Padrão prefixo*
                        prefix = pattern[:-1]
                        if item_name.startswith(prefix):
                            should_backup = True
                            break
                    else:
                        # Padrão exato
                        if item_name == pattern:
                            should_backup = True
                            break
            
            if should_backup:
                files_to_backup.append(item)
            else:
                # Se não é core nem backup, considerar como "outros"
                if item_name not in ['backup_arquivos_nao_core']:
                    core_files.append(item)
        
        return files_to_backup, core_files
    
    def move_to_backup(self, items: List[Path]) -> Dict[str, int]:
        """
        Move items para diretório de backup
        
        Args:
            items: Lista de caminhos para mover
            
        Returns:
            Dict com estatísticas da movimentação
        """
        stats = {'files': 0, 'directories': 0, 'errors': 0}
        
        for item in items:
            try:
                destination = self.backup_dir / item.name
                
                # Se destino já existe, criar nome único
                counter = 1
                original_destination = destination
                while destination.exists():
                    if item.is_dir():
                        destination = self.backup_dir / f"{item.name}_{counter}"
                    else:
                        stem = item.stem
                        suffix = item.suffix
                        destination = self.backup_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Mover arquivo ou diretório
                shutil.move(str(item), str(destination))
                
                if item.is_dir():
                    stats['directories'] += 1
                    print(f"📁 Movido diretório: {item.name} → backup/")
                else:
                    stats['files'] += 1
                    print(f"📄 Movido arquivo: {item.name} → backup/")
                
            except Exception as e:
                stats['errors'] += 1
                print(f"❌ Erro ao mover {item.name}: {e}")
        
        return stats
    
    def generate_report(self, files_to_backup: List[Path], core_files: List[Path], 
                       stats: Dict[str, int]) -> str:
        """
        Gera relatório da sanitização
        
        Returns:
            str: Relatório formatado
        """
        report = [
            "# 🧹 RELATÓRIO DE SANITIZAÇÃO - DINO ARC",
            "",
            f"## 📊 Resumo da Operação",
            f"- **Arquivos movidos para backup**: {stats['files']}",
            f"- **Diretórios movidos para backup**: {stats['directories']}",
            f"- **Erros**: {stats['errors']}",
            f"- **Arquivos core mantidos**: {len(core_files)}",
            "",
            "## 📁 Arquivos Core Mantidos",
        ]
        
        for item in sorted(core_files):
            if item.is_dir():
                report.append(f"- 📁 {item.name}/")
            else:
                report.append(f"- 📄 {item.name}")
        
        report.extend([
            "",
            "## 🗃️ Arquivos Movidos para Backup",
        ])
        
        for item in sorted(files_to_backup):
            if item.is_dir():
                report.append(f"- 📁 {item.name}/")
            else:
                report.append(f"- 📄 {item.name}")
        
        report.extend([
            "",
            "## 🎯 Estrutura Final do Projeto",
            "",
            "```",
            "dino_arc/",
            "├── src/                    # 📦 Código fonte principal",
            "│   ├── cli.py             # 🖥️ CLI principal",
            "│   ├── sdk/               # 🔧 Módulos SDK",
            "│   └── databricks_config/ # ⚙️ Configuração Databricks",
            "├── terraform/             # 🏗️ Infraestrutura como código",
            "├── backup_arquivos_nao_core/ # 🗃️ Arquivos movidos",
            "├── setup.py               # ⚙️ Configuração do pacote",
            "├── requirements.txt       # 📋 Dependências",
            "├── README.md              # 📖 Documentação principal",
            "└── pyproject.toml         # 🔧 Configuração do projeto",
            "```",
            "",
            "## ✅ Projeto Sanitizado com Sucesso!",
            "",
            f"O projeto dino_arc agora contém apenas os arquivos essenciais.",
            f"Todos os arquivos auxiliares estão em `backup_arquivos_nao_core/`.",
            "",
            "### 🚀 Próximos Passos:",
            "1. Verificar se todos os imports estão funcionando",
            "2. Executar testes básicos do CLI",
            "3. Validar funcionamento da aplicação",
            "",
            f"**Data da sanitização**: {Path(__file__).stat().st_mtime}",
        ])
        
        return "\\n".join(report)
    
    def sanitize(self, dry_run: bool = False, auto_confirm: bool = False) -> bool:
        """
        Executa a sanitização completa
        
        Args:
            dry_run: Se True, apenas simula sem mover arquivos
            auto_confirm: Se True, confirma automaticamente
            
        Returns:
            bool: True se bem-sucedida
        """
        print("🧹 Iniciando sanitização do projeto Dino ARC...")
        print(f"📁 Diretório do projeto: {self.project_root}")
        
        # Identificar arquivos
        files_to_backup, core_files = self.identify_files_to_backup()
        
        print(f"\\n📊 Análise concluída:")
        print(f"   - Arquivos core (manter): {len(core_files)}")
        print(f"   - Arquivos para backup: {len(files_to_backup)}")
        
        if dry_run:
            print("\\n🔍 MODO DRY-RUN - Apenas simulação:")
            print("\\n📁 Arquivos que seriam movidos para backup:")
            for item in files_to_backup:
                print(f"   → {item.name}")
            return True
        
        # Confirmar ação
        print("\\n⚠️  Esta operação moverá arquivos para backup.")
        print("   Arquivos core serão mantidos no projeto.")
        response = input("Continuar com a sanitização? (s/N): ").lower().strip()
        
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada pelo usuário.")
            return False
        
        # Criar diretório de backup
        if not self.create_backup_directory():
            return False
        
        # Mover arquivos
        print("\\n🚀 Iniciando movimentação de arquivos...")
        stats = self.move_to_backup(files_to_backup)
        
        # Gerar relatório
        report = self.generate_report(files_to_backup, core_files, stats)
        
        # Salvar relatório
        report_file = self.project_root / "RELATORIO_SANITIZACAO_FINAL.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\\n📝 Relatório salvo em: {report_file}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar relatório: {e}")
        
        # Mostrar resultado
        print("\\n🎉 Sanitização concluída!")
        print(f"   ✅ {stats['files']} arquivos movidos")
        print(f"   ✅ {stats['directories']} diretórios movidos")
        if stats['errors'] > 0:
            print(f"   ⚠️  {stats['errors']} erros encontrados")
        
        print(f"\\n📁 Arquivos movidos para: {self.backup_dir}")
        print("📋 Verifique o relatório para detalhes completos.")
        
        return stats['errors'] == 0


def main():
    """
    Função principal do script
    """
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("🧹 Dino ARC Project Sanitizer")
        print("")
        print("Usage:")
        print("  python sanitize_project.py [--dry-run] [--auto-confirm]")
        print("")
        print("Options:")
        print("  --dry-run        Simula a operação sem mover arquivos")
        print("  --auto-confirm   Confirma automaticamente sem perguntar")
        print("  --help           Mostra esta ajuda")
        return
    
    # Detectar diretório do projeto
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    # Verificar se estamos no diretório correto
    if not (project_root / "setup.py").exists():
        print("❌ Erro: Execute este script na raiz do projeto dino_arc")
        print(f"   Diretório atual: {project_root}")
        print("   Esperado encontrar: setup.py")
        sys.exit(1)
    
    # Verificar se dry-run foi solicitado
    dry_run = '--dry-run' in sys.argv
    auto_confirm = '--auto-confirm' in sys.argv
    
    # Executar sanitização
    sanitizer = DinoArcSanitizer(str(project_root))
    success = sanitizer.sanitize(dry_run=dry_run, auto_confirm=auto_confirm)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
