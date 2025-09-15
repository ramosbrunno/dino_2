# Databricks Configuration Scripts

Este diretório contém scripts para configuração automática do Databricks Unity Catalog e recursos Serverless após o deploy da infraestrutura via Terraform.

## Arquivos

### 1. `unity_catalog_setup.py`
Script Python completo para configuração do Unity Catalog e Serverless com classe reutilizável.

**Recursos:**
- ✅ Criação do Unity Catalog Metastore
- ✅ Atribuição do Metastore ao Workspace
- ✅ Criação de Catalog principal do projeto
- ✅ Criação de Schemas (bronze, silver, gold, workspace)
- ✅ Habilitação do Serverless Compute
- ✅ Criação de SQL Warehouse Serverless
- ✅ Configuração completa automatizada

**Dependências Python:**
```bash
pip install requests
```

### 2. `setup_databricks.sh`
Script Shell (Linux/MacOS) para configuração via API REST do Databricks.

**Dependências:**
- `curl` - para requisições HTTP
- `jq` - para processamento JSON

**Instalação das dependências:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install curl jq

# MacOS
brew install curl jq

# CentOS/RHEL
sudo yum install curl jq
```

### 3. `setup_databricks.bat`
Script Batch (Windows) para configuração via API REST do Databricks.

**Dependências:**
- `curl` - incluído no Windows 10+
- `jq` - download em https://stedolan.github.io/jq/download/

## Variáveis de Ambiente Necessárias

Todas as versões dos scripts requerem as seguintes variáveis de ambiente:

```bash
# URL do workspace Databricks (obtido via Terraform output)
export DATABRICKS_WORKSPACE_URL="https://adb-1234567890123456.78.azuredatabricks.net"

# Token de acesso (gerado no Databricks ou via Service Principal)
export DATABRICKS_ACCESS_TOKEN="dapi1234567890abcdef..."

# Root storage para Unity Catalog (obtido via Terraform output)
export UNITY_CATALOG_STORAGE_ROOT="abfss://unity-catalog@storageaccount.dfs.core.windows.net/"

# ID do workspace Databricks (obtido via Terraform output)
export DATABRICKS_WORKSPACE_ID="1234567890123456"

# Parâmetros do projeto
export PROJETO="meu-projeto"
export AMBIENTE="dev"
export AZURE_REGION="East US"
```

## Como Usar

### Opção 1: Script Python
```bash
# Instalar dependências
pip install requests

# Configurar variáveis de ambiente
export DATABRICKS_WORKSPACE_URL="..."
export DATABRICKS_ACCESS_TOKEN="..."
# ... outras variáveis

# Executar
python unity_catalog_setup.py
```

### Opção 2: Script Shell (Linux/MacOS)
```bash
# Dar permissão de execução
chmod +x setup_databricks.sh

# Configurar variáveis de ambiente
export DATABRICKS_WORKSPACE_URL="..."
# ... outras variáveis

# Executar
./setup_databricks.sh
```

### Opção 3: Script Batch (Windows)
```cmd
REM Configurar variáveis de ambiente
set DATABRICKS_WORKSPACE_URL=...
set DATABRICKS_ACCESS_TOKEN=...
REM ... outras variáveis

REM Executar
setup_databricks.bat
```

## Integração com Terraform

Os scripts podem ser executados automaticamente após o deploy do Terraform usando `local-exec` provisioner:

```hcl
resource "null_resource" "databricks_config" {
  depends_on = [azurerm_databricks_workspace.main]

  provisioner "local-exec" {
    command = "python ${path.module}/databricks_config/unity_catalog_setup.py"
    
    environment = {
      DATABRICKS_WORKSPACE_URL      = "https://${azurerm_databricks_workspace.main.workspace_url}"
      DATABRICKS_ACCESS_TOKEN       = var.databricks_token
      UNITY_CATALOG_STORAGE_ROOT    = "abfss://${azurerm_storage_container.unity_catalog.name}@${azurerm_storage_account.unity_catalog.name}.dfs.core.windows.net/"
      DATABRICKS_WORKSPACE_ID       = azurerm_databricks_workspace.main.workspace_id
      PROJETO                       = var.projeto
      AMBIENTE                      = var.ambiente
      AZURE_REGION                  = var.location
    }
  }
}
```

## Recursos Criados

Após a execução dos scripts, serão criados:

### Unity Catalog
- **Metastore**: `unity-catalog-{region}`
- **Catalog**: `{projeto}_{ambiente}`
- **Schemas**:
  - `bronze` - Dados brutos
  - `silver` - Dados processados
  - `gold` - Dados refinados
  - `workspace` - Dados de workspace

### Serverless
- **Compute**: Habilitado para o workspace
- **SQL Warehouse**: `{projeto}-{ambiente}-warehouse`
  - Tamanho: 2X-Small
  - Auto-stop: 10 minutos
  - Photon habilitado
  - Spot instances para otimização de custos

## Troubleshooting

### Erro: "Import requests could not be resolved"
```bash
pip install requests
```

### Erro: "curl command not found"
```bash
# Ubuntu/Debian
sudo apt-get install curl

# CentOS/RHEL
sudo yum install curl
```

### Erro: "jq command not found"
```bash
# Ubuntu/Debian
sudo apt-get install jq

# MacOS
brew install jq

# Windows: Download em https://stedolan.github.io/jq/download/
```

### Erro: "Unauthorized" (401)
- Verificar se o `DATABRICKS_ACCESS_TOKEN` está correto
- Verificar se o token tem permissões de administrador
- Verificar se o workspace URL está correto

### Erro: "Metastore already exists"
- Normal se executar o script novamente
- O script tentará usar o metastore existente

## Logs e Monitoramento

Os scripts fornecem logs detalhados durante a execução:
- ✅ Operações bem-sucedidas
- ⚠️ Avisos (recursos já existentes)
- ❌ Erros com detalhes da API
- 📋 Resumo final da configuração

## Segurança

**⚠️ Importante:**
- Nunca commitar tokens de acesso no código
- Usar variáveis de ambiente ou Azure Key Vault
- Limitar permissões do token ao mínimo necessário
- Rotacionar tokens regularmente
