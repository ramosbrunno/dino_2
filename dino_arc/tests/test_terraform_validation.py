"""
Testes para validação dos arquivos Terraform
"""
import unittest
import os
import re
import json


class TestTerraformFiles(unittest.TestCase):
    """Testes para validar a estrutura e conteúdo dos arquivos Terraform"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.terraform_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'terraform')
        self.modules_dir = os.path.join(self.terraform_dir, 'modules')
    
    def test_terraform_files_exist(self):
        """Testa se os arquivos principais do Terraform existem"""
        required_files = [
            'main.tf',
            'variables.tf',
            'outputs.tf',
            'terraform.tfvars.example'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(self.terraform_dir, file_name)
            with self.subTest(file=file_name):
                self.assertTrue(os.path.exists(file_path), f"Arquivo {file_name} não encontrado")
    
    def test_module_files_exist(self):
        """Testa se os arquivos dos módulos existem"""
        modules = ['foundation', 'databricks']
        required_module_files = ['main.tf', 'variables.tf', 'outputs.tf']
        
        for module in modules:
            module_path = os.path.join(self.modules_dir, module)
            with self.subTest(module=module):
                self.assertTrue(os.path.exists(module_path), f"Módulo {module} não encontrado")
                
                for file_name in required_module_files:
                    file_path = os.path.join(module_path, file_name)
                    with self.subTest(module=module, file=file_name):
                        self.assertTrue(os.path.exists(file_path), 
                                      f"Arquivo {file_name} não encontrado no módulo {module}")
    
    def test_main_tf_syntax(self):
        """Testa a sintaxe básica do main.tf"""
        main_tf_path = os.path.join(self.terraform_dir, 'main.tf')
        
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém os providers necessários
        self.assertIn('azurerm', content, "Provider azurerm não encontrado")
        self.assertIn('azuread', content, "Provider azuread não encontrado")
        self.assertIn('random', content, "Provider random não encontrado")
        
        # Verificar se contém os módulos
        self.assertIn('module "foundation"', content, "Módulo foundation não encontrado")
        self.assertIn('module "databricks"', content, "Módulo databricks não encontrado")
        
        # Verificar se não há referências a variáveis opcionais removidas
        self.assertNotIn('var.enable_databricks', content, 
                        "Variável enable_databricks ainda presente (deveria ter sido removida)")
    
    def test_variables_tf_structure(self):
        """Testa a estrutura do variables.tf"""
        variables_tf_path = os.path.join(self.terraform_dir, 'variables.tf')
        
        with open(variables_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém as variáveis essenciais
        essential_vars = ['projeto', 'ambiente', 'location', 'tags']
        
        for var in essential_vars:
            with self.subTest(variable=var):
                self.assertIn(f'variable "{var}"', content, f"Variável {var} não encontrada")
        
        # Verificar se não contém variáveis opcionais removidas
        removed_vars = ['enable_databricks', 'enable_foundation']
        
        for var in removed_vars:
            with self.subTest(variable=var):
                self.assertNotIn(f'variable "{var}"', content, 
                               f"Variável {var} ainda presente (deveria ter sido removida)")
    
    def test_outputs_tf_structure(self):
        """Testa a estrutura do outputs.tf"""
        outputs_tf_path = os.path.join(self.terraform_dir, 'outputs.tf')
        
        with open(outputs_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém os outputs essenciais
        essential_outputs = [
            'databricks_workspace_url',
            'databricks_workspace_id',
            'unity_catalog_storage_root',
            'databricks_access_token'
        ]
        
        for output in essential_outputs:
            with self.subTest(output=output):
                self.assertIn(f'output "{output}"', content, f"Output {output} não encontrado")
        
        # Verificar se o token é marcado como sensível
        self.assertIn('sensitive   = true', content, 
                     "Token de acesso não marcado como sensível")
    
    def test_foundation_module_structure(self):
        """Testa a estrutura do módulo foundation"""
        foundation_main = os.path.join(self.modules_dir, 'foundation', 'main.tf')
        
        with open(foundation_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar recursos essenciais
        essential_resources = [
            'azurerm_resource_group',
            'azurerm_key_vault',
            'azuread_application',
            'azuread_service_principal'
        ]
        
        for resource in essential_resources:
            with self.subTest(resource=resource):
                self.assertIn(resource, content, f"Recurso {resource} não encontrado")
    
    def test_databricks_module_structure(self):
        """Testa a estrutura do módulo databricks"""
        databricks_main = os.path.join(self.modules_dir, 'databricks', 'main.tf')
        
        with open(databricks_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar recursos essenciais
        essential_resources = [
            'azurerm_databricks_workspace',
            'azurerm_storage_account',
            'azurerm_storage_container'
        ]
        
        for resource in essential_resources:
            with self.subTest(resource=resource):
                self.assertIn(resource, content, f"Recurso {resource} não encontrado")
        
        # Verificar configurações específicas
        self.assertIn('sku                         = "premium"', content, 
                     "SKU Premium não configurado")
        self.assertIn('is_hns_enabled', content, 
                     "Hierarchical namespace não configurado")
    
    def test_terraform_tfvars_example(self):
        """Testa o arquivo de exemplo de variáveis"""
        tfvars_example = os.path.join(self.terraform_dir, 'terraform.tfvars.example')
        
        with open(tfvars_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém exemplos das variáveis essenciais
        essential_examples = ['projeto', 'ambiente', 'location']
        
        for example in essential_examples:
            with self.subTest(example=example):
                self.assertIn(example, content, f"Exemplo para {example} não encontrado")
    
    def test_no_hardcoded_values(self):
        """Testa se não há valores hardcoded nos arquivos Terraform"""
        terraform_files = []
        
        # Coletar todos os arquivos .tf
        for root, dirs, files in os.walk(self.terraform_dir):
            for file in files:
                if file.endswith('.tf'):
                    terraform_files.append(os.path.join(root, file))
        
        # Padrões que não devem estar presentes (valores hardcoded)
        forbidden_patterns = [
            r'subscription_id\s*=\s*"[^"]*"',  # subscription_id hardcoded
            r'tenant_id\s*=\s*"[^"]*"',        # tenant_id hardcoded (exceto em exemplos)
            r'client_id\s*=\s*"[^"]*"',        # client_id hardcoded
            r'client_secret\s*=\s*"[^"]*"'     # client_secret hardcoded
        ]
        
        for tf_file in terraform_files:
            if 'example' in tf_file:  # Pular arquivos de exemplo
                continue
                
            with open(tf_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in forbidden_patterns:
                with self.subTest(file=tf_file, pattern=pattern):
                    matches = re.search(pattern, content, re.IGNORECASE)
                    self.assertIsNone(matches, 
                                    f"Valor hardcoded encontrado em {tf_file}: {pattern}")
    
    def test_consistent_naming_convention(self):
        """Testa se a convenção de nomenclatura está consistente"""
        main_tf_path = os.path.join(self.terraform_dir, 'main.tf')
        
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar padrão de nomenclatura: projeto-ambiente-sufixo
        naming_patterns = [
            r'\$\{var\.projeto\}-\$\{var\.ambiente\}',  # Padrão básico
            r'projeto.*ambiente',                        # Uso das variáveis
        ]
        
        pattern_found = False
        for pattern in naming_patterns:
            if re.search(pattern, content):
                pattern_found = True
                break
        
        self.assertTrue(pattern_found, "Padrão de nomenclatura não encontrado")


class TestTerraformConfiguration(unittest.TestCase):
    """Testes para configurações específicas do Terraform"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.terraform_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'terraform')
    
    def test_provider_versions(self):
        """Testa se as versões dos providers estão especificadas"""
        main_tf_path = os.path.join(self.terraform_dir, 'main.tf')
        
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar versões dos providers
        provider_versions = [
            (r'azurerm.*version.*~>\s*3\.0', 'azurerm'),
            (r'azuread.*version.*~>\s*2\.0', 'azuread'),
            (r'random.*version.*~>\s*3\.0', 'random')
        ]
        
        for pattern, provider in provider_versions:
            with self.subTest(provider=provider):
                self.assertRegex(content, pattern, 
                               f"Versão do provider {provider} não especificada corretamente")
    
    def test_terraform_version_requirement(self):
        """Testa se a versão mínima do Terraform está especificada"""
        main_tf_path = os.path.join(self.terraform_dir, 'main.tf')
        
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar versão mínima do Terraform
        version_pattern = r'required_version\s*=\s*">=\s*1\.0"'
        self.assertRegex(content, version_pattern, 
                        "Versão mínima do Terraform não especificada corretamente")
    
    def test_network_watcher_disabled(self):
        """Testa se o Network Watcher está desabilitado"""
        main_tf_path = os.path.join(self.terraform_dir, 'main.tf')
        
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se Network Watcher está desabilitado
        self.assertIn('disable_network_watcher', content, 
                     "Configuração para desabilitar Network Watcher não encontrada")


if __name__ == '__main__':
    unittest.main()
