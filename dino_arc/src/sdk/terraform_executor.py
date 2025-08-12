import os
import subprocess
import json
from typing import Dict, Optional, Any

class TerraformExecutor:
    def __init__(self):
        self.working_directory = os.path.join(os.path.dirname(__file__), "../terraform")
    
    def init(self):
        """Inicializa o Terraform - não aceita variáveis"""
        result = subprocess.run(
            ["terraform", "init"], 
            cwd=self.working_directory,
            capture_output=True,
            text=True
        )
        return result
    
    def apply(self, variables: Optional[Dict[str, Any]] = None, var_file: Optional[str] = None):
        """
        Aplica configuração Terraform com variáveis opcionais
        
        Args:
            variables: Dicionário com variáveis (ex: {"resource_group_name": "meu-rg"})
            var_file: Caminho para arquivo .tfvars
        """
        cmd = ["terraform", "apply", "-auto-approve"]
        
        # Adiciona variáveis individuais usando -var
        if variables:
            for key, value in variables.items():
                if isinstance(value, dict):
                    # Para objetos complexos como tags, converta para JSON
                    value = json.dumps(value)
                cmd.extend(["-var", f"{key}={value}"])
        
        # Adiciona arquivo de variáveis
        if var_file:
            cmd.extend(["-var-file", var_file])
        
        result = subprocess.run(
            cmd, 
            cwd=self.working_directory,
            capture_output=True,
            text=True
        )
        return result
    
    def apply_with_env_vars(self, env_variables: Optional[Dict[str, str]] = None):
        """
        Aplica usando variáveis de ambiente TF_VAR_*
        
        Args:
            env_variables: Dicionário com variáveis de ambiente
        """
        env = os.environ.copy()
        
        if env_variables:
            for key, value in env_variables.items():
                env[f"TF_VAR_{key}"] = str(value)
        
        result = subprocess.run([
            "terraform", "apply", "-auto-approve"
        ], cwd=self.working_directory, env=env, capture_output=True, text=True)
        return result
    
    def plan(self, variables: Optional[Dict[str, Any]] = None, var_file: Optional[str] = None):
        """
        Executa terraform plan com variáveis opcionais
        """
        cmd = ["terraform", "plan"]
        
        if variables:
            for key, value in variables.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                cmd.extend(["-var", f"{key}={value}"])
        
        if var_file:
            cmd.extend(["-var-file", var_file])
        
        result = subprocess.run(
            cmd, 
            cwd=self.working_directory,
            capture_output=True,
            text=True
        )
        return result
    
    def destroy(self, variables: Optional[Dict[str, Any]] = None, var_file: Optional[str] = None):
        """
        Destrói recursos com variáveis opcionais
        """
        cmd = ["terraform", "destroy", "-auto-approve"]
        
        if variables:
            for key, value in variables.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                cmd.extend(["-var", f"{key}={value}"])
        
        if var_file:
            cmd.extend(["-var-file", var_file])
        
        result = subprocess.run(
            cmd, 
            cwd=self.working_directory,
            capture_output=True,
            text=True
        )
        return result