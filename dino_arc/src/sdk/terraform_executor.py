"""
Terraform Executor Module for Dino ARC
Handles Terraform operations (init, plan, apply, destroy)
"""

import os
import subprocess
import json
import tempfile
from typing import Dict, Optional, Any, List
from pathlib import Path


class TerraformExecutor:
    """
    Classe para executar comandos Terraform de forma controlada
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        """
        Inicializa o Terraform Executor
        
        Args:
            working_dir: Diretório de trabalho para comandos Terraform (padrão: src/terraform)
        """
        if working_dir:
            self.working_dir = Path(working_dir)
        else:
            # Detectar diretório terraform baseado na localização do script
            script_dir = Path(__file__).parent.parent
            self.working_dir = script_dir / "terraform"
        
        self.working_dir = self.working_dir.resolve()
        self._initialized = False
    
    def _run_terraform_command(self, command: List[str], env_vars: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Executa comando Terraform com configurações padrão
        
        Args:
            command: Lista com comando terraform
            env_vars: Variáveis de ambiente adicionais
            
        Returns:
            subprocess.CompletedProcess: Resultado da execução
        """
        # Configurar ambiente
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        # Garantir que o diretório existe
        if not self.working_dir.exists():
            raise FileNotFoundError(f"Diretório Terraform não encontrado: {self.working_dir}")
        
        # Executar comando
        return subprocess.run(
            command,
            cwd=self.working_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutos timeout
        )
    
    def init(self) -> subprocess.CompletedProcess:
        """
        Inicializa Terraform no diretório de trabalho
        
        Returns:
            subprocess.CompletedProcess: Resultado da inicialização
        """
        print("🔧 Inicializando Terraform...")
        
        command = ["terraform", "init", "-upgrade"]
        result = self._run_terraform_command(command)
        
        if result.returncode == 0:
            self._initialized = True
            print("✅ Terraform inicializado com sucesso!")
        else:
            print(f"❌ Erro na inicialização do Terraform: {result.stderr}")
        
        return result
    
    def plan(self, variables: Optional[Dict[str, str]] = None, out_file: str = "tfplan") -> subprocess.CompletedProcess:
        """
        Executa terraform plan
        
        Args:
            variables: Variáveis para o Terraform
            out_file: Arquivo de saída do plano
            
        Returns:
            subprocess.CompletedProcess: Resultado do planejamento
        """
        print("📋 Executando planejamento Terraform...")
        
        command = ["terraform", "plan", f"-out={out_file}"]
        
        # Adicionar variáveis como argumentos
        if variables:
            for key, value in variables.items():
                command.extend(["-var", f"{key}={value}"])
        
        result = self._run_terraform_command(command)
        
        if result.returncode == 0:
            print("✅ Planejamento concluído com sucesso!")
        else:
            print(f"❌ Erro no planejamento: {result.stderr}")
        
        return result
    
    def apply(self, variables: Optional[Dict[str, str]] = None, plan_file: str = "tfplan", auto_approve: bool = True) -> subprocess.CompletedProcess:
        """
        Executa terraform apply
        
        Args:
            variables: Variáveis para o Terraform
            plan_file: Arquivo de plano a aplicar
            auto_approve: Auto-aprovar mudanças
            
        Returns:
            subprocess.CompletedProcess: Resultado da aplicação
        """
        print("🏗️ Aplicando infraestrutura Terraform...")
        
        # Se há arquivo de plano, usar ele
        plan_path = self.working_dir / plan_file
        if plan_path.exists():
            command = ["terraform", "apply"]
            if auto_approve:
                command.append("-auto-approve")
            command.append(plan_file)
        else:
            # Aplicar diretamente
            command = ["terraform", "apply"]
            if auto_approve:
                command.append("-auto-approve")
            
            # Adicionar variáveis
            if variables:
                for key, value in variables.items():
                    command.extend(["-var", f"{key}={value}"])
        
        result = self._run_terraform_command(command)
        
        if result.returncode == 0:
            print("✅ Infraestrutura aplicada com sucesso!")
        else:
            print(f"❌ Erro na aplicação: {result.stderr}")
        
        return result
    
    def destroy(self, variables: Optional[Dict[str, str]] = None, auto_approve: bool = True) -> subprocess.CompletedProcess:
        """
        Executa terraform destroy
        
        Args:
            variables: Variáveis para o Terraform
            auto_approve: Auto-aprovar destruição
            
        Returns:
            subprocess.CompletedProcess: Resultado da destruição
        """
        print("🗑️ Destruindo infraestrutura Terraform...")
        
        command = ["terraform", "destroy"]
        if auto_approve:
            command.append("-auto-approve")
        
        # Adicionar variáveis
        if variables:
            for key, value in variables.items():
                command.extend(["-var", f"{key}={value}"])
        
        result = self._run_terraform_command(command)
        
        if result.returncode == 0:
            print("✅ Infraestrutura destruída com sucesso!")
        else:
            print(f"❌ Erro na destruição: {result.stderr}")
        
        return result
    
    def get_outputs(self) -> Dict[str, Any]:
        """
        Obtém outputs do Terraform state
        
        Returns:
            Dict: Outputs do Terraform
        """
        try:
            command = ["terraform", "output", "-json"]
            result = self._run_terraform_command(command)
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            else:
                print(f"❌ Erro ao obter outputs: {result.stderr}")
                return {}
                
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar outputs JSON: {e}")
            return {}
        except Exception as e:
            print(f"❌ Erro inesperado ao obter outputs: {e}")
            return {}
    
    def validate(self) -> subprocess.CompletedProcess:
        """
        Valida configuração Terraform
        
        Returns:
            subprocess.CompletedProcess: Resultado da validação
        """
        print("✅ Validando configuração Terraform...")
        
        command = ["terraform", "validate"]
        result = self._run_terraform_command(command)
        
        if result.returncode == 0:
            print("✅ Configuração Terraform válida!")
        else:
            print(f"❌ Configuração inválida: {result.stderr}")
        
        return result
    
    def is_initialized(self) -> bool:
        """
        Verifica se Terraform está inicializado
        
        Returns:
            bool: True se inicializado
        """
        terraform_dir = self.working_dir / ".terraform"
        return terraform_dir.exists() and self._initialized
    
    def get_working_directory(self) -> Path:
        """
        Retorna diretório de trabalho atual
        
        Returns:
            Path: Caminho do diretório
        """
        return self.working_dir
