# DINO ARC v2.0.0

Ferramenta CLI para criação automatizada de infraestrutura Azure com Databricks Premium, Unity Catalog e Serverless Computing usando autenticação Service Principal (SPN) via Terraform.

## ⚡ Setup Rápido

### Opção 1: Setup Automático (Recomendado)
```bash
# Execute o script de setup que instala tudo automaticamente
setup-env.bat
```

### Opção 2: Setup Manual

#### 1. Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv dino_env

# Ativar ambiente virtual (Windows)
dino_env\Scripts\activate
```

#### 2. Instalar DINO ARC
```bash
# Instalar em modo desenvolvimento
pip install -e .
```

#### 3. Instalar Terraform

O Terraform é obrigatório para funcionamento do DINO ARC. Escolha uma das opções abaixo:

**Opção A: Windows com winget (Recomendado para Windows 10/11)**
```bash
winget install HashiCorp.Terraform
```

**Opção B: Windows com Chocolatey**
```bash
# Instalar Chocolatey primeiro (se não tiver)
# https://chocolatey.org/install

# Instalar Terraform
choco install terraform
```

**Opção C: Download Manual (Funciona em qualquer sistema)**
```bash
# 1. Baixar o Terraform do site oficial
# https://www.terraform.io/downloads.html

# 2. Extrair o arquivo baixado
# 3. Colocar o executável terraform.exe em uma pasta no PATH
# 4. Ou criar uma pasta local (exemplo: C:\terraform) e adicionar ao PATH
```

**Opção D: PowerShell Download Automático (Windows)**
```powershell
# Criar pasta para o Terraform
mkdir C:\terraform
cd C:\terraform

# Baixar e extrair
Invoke-WebRequest -Uri "https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_windows_amd64.zip" -OutFile "terraform.zip"
Expand-Archive -Path "terraform.zip" -DestinationPath "C:\terraform"
Remove-Item "terraform.zip"

# Adicionar ao PATH (permanente)
$env:PATH += ";C:\terraform"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::User)
```

**⚡ Script Automático para Terraform (Se tiver problemas)**
```bash
# Execute este script que tenta vários métodos de instalação
install-terraform.bat
```

**📋 Verificar Instalação do Terraform**
```bash
# Abra um novo terminal e teste
terraform version

# Deve retornar algo como:
# Terraform v1.6.6
```

**⚠️ Importante:** 
- Após instalar via winget ou chocolatey, **reinicie o terminal** ou abra um novo
- Se ainda não funcionar, reinicie o computador para atualizar o PATH
- Para verificar se está no PATH: `echo $env:PATH` (PowerShell) ou `echo %PATH%` (CMD)

#### 4. Verificar Instalação
```bash
# Testar DINO ARC
dino_arc --help

# Verificar Terraform
terraform version
```

## 🚀 Uso

### Autenticação via Service Principal

Você precisa dos seguintes parâmetros do Azure:
- **Client ID**: ID do Service Principal
- **Client Secret**: Secret do Service Principal  
- **Tenant ID**: ID do Tenant Azure
- **Subscription ID**: ID da Subscription Azure

### Criar Infraestrutura Completa

**⚠️ IMPORTANTE - Segurança das Credenciais:**
- **NUNCA** commite credenciais reais no código
- Use variáveis de ambiente para produção
- Mantenha secrets seguros no Azure Key Vault
- Revogue credenciais se expostas acidentalmente

```bash
dino_arc \
  --client-id "your-client-id" \
  --client-secret "your-client-secret" \
  --tenant-id "your-tenant-id" \
  --subscription-id "your-subscription-id" \
  --action apply \
  --projeto dino \
  --ambiente dev
```

### Usar Variáveis de Ambiente (Recomendado para Produção)

Para maior segurança, configure as credenciais como variáveis de ambiente:

```bash
# Configurar variáveis (Windows CMD)
set ARM_CLIENT_ID=your-client-id
set ARM_CLIENT_SECRET=your-client-secret
set ARM_TENANT_ID=your-tenant-id
set ARM_SUBSCRIPTION_ID=your-subscription-id

# Executar sem expor credenciais na linha de comando
dino_arc --action apply --projeto meuapp --ambiente prod
```

```powershell
# Configurar variáveis (PowerShell)
$env:ARM_CLIENT_ID="your-client-id"
$env:ARM_CLIENT_SECRET="your-client-secret"
$env:ARM_TENANT_ID="your-tenant-id"
$env:ARM_SUBSCRIPTION_ID="your-subscription-id"

# Executar
dino_arc --action apply --projeto meuapp --ambiente prod
```

### Exemplo com Parâmetros Fictícios
```bash
dino_arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "ExEmPlO~SeCrEt1234567890abcdefghij" \
  --tenant-id "87654321-4321-4321-4321-210987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action apply \
  --projeto meuapp \
  --ambiente dev
```

## 🎯 Recursos Criados

O DINO ARC cria automaticamente:

- ✅ **Resource Group**: `{projeto}-{ambiente}-rsg`
- ✅ **Key Vault**: Para armazenamento seguro de secrets
- ✅ **Service Principal**: Para autenticação automatizada
- ✅ **Azure SQL Database**: Para logs e metadados
- ✅ **Databricks Workspace Premium**: Com todas as funcionalidades
- ✅ **Unity Catalog**: Metastore e catálogos configurados
- ✅ **Serverless Computing**: Habilitado automaticamente

## 🔧 Parâmetros

| Parâmetro | Descrição | Obrigatório | Padrão |
|-----------|-----------|-------------|---------|
| `--client-id` | Azure Service Principal Client ID | ✅ | - |
| `--client-secret` | Azure Service Principal Client Secret | ✅ | - |
| `--tenant-id` | Azure Tenant ID | ✅ | - |
| `--subscription-id` | Azure Subscription ID | ✅ | - |
| `--action` | Ação a executar (apply) | ✅ | - |
| `--projeto` | Nome do projeto | ✅ | - |
| `--ambiente` | Ambiente (dev/prod) | ✅ | - |
| `--location` | Região Azure | ❌ | East US 2 |

## 📋 Pré-requisitos

### Obrigatórios
- **Python 3.8+**: Para executar o DINO ARC
- **Terraform 1.0+**: Para provisionar a infraestrutura Azure
- **Service Principal Azure**: Com permissões adequadas na subscription
- **Acesso à Azure Subscription**: Para criar recursos

### Verificar Pré-requisitos
```bash
# Verificar Python
python --version

# Verificar Terraform (OBRIGATÓRIO)
terraform version

# Se algum comando falhar, instale seguindo as instruções acima
```

### Permissões do Service Principal
O Service Principal precisa das seguintes permissões na subscription:
- `Contributor`: Para criar e gerenciar recursos
- `User Access Administrator`: Para atribuir permissões ao Databricks
- `Storage Blob Data Contributor`: Para Unity Catalog

## � Troubleshooting

### ❌ "terraform não é reconhecido como comando"

**Problema**: Terraform foi instalado mas não está no PATH

**Soluções**:
```bash
# 1. Reinicie o terminal/prompt de comando
# 2. Ou reinicie o computador
# 3. Ou execute o script automático:
install-terraform.bat

# 4. Verificar se está instalado:
where terraform

# 5. Se instalou via winget/choco, aguarde alguns minutos e tente novamente
```

### ❌ "winget install falhou"

**Problema**: winget não conseguiu instalar o Terraform

**Soluções**:
```bash
# Use o script que tenta múltiplos métodos:
install-terraform.bat

# Ou instale manualmente:
# 1. Baixe de: https://www.terraform.io/downloads.html
# 2. Extraia em C:\terraform
# 3. Adicione C:\terraform ao PATH
```

### ❌ "pip install -e . falhou"

**Problema**: Erro na instalação do pacote Python

**Soluções**:
```bash
# 1. Certifique-se que está no ambiente virtual
dino_env\Scripts\activate

# 2. Atualize pip
python -m pip install --upgrade pip

# 3. Instale novamente
pip install -e .
```

### ❌ "Service Principal sem permissões"

**Problema**: Erros de autorização ao criar recursos

**Soluções**:
- Verifique se o SPN tem role `Contributor` na subscription
- Adicione role `User Access Administrator` para Databricks
- Consulte a documentação Azure sobre Service Principals

## �🔐 Segurança

- Autenticação via Service Principal (SPN)
- Secrets mascarados no output
- Variáveis de ambiente seguras para Terraform
- Key Vault para armazenamento de credenciais
  --action destroy \
  --projeto myapp \
  --ambiente dev
```

### Ajuda
```bash
dino_arc --help
```

## O Que É Criado

- Resource Group do Azure
- Azure Key Vault
- Service Principal
- Azure SQL Database
- Databricks Premium Workspace
- Unity Catalog com Metastore
- Serverless Computing (habilitado automaticamente)

## Requisitos

- Python 3.8+
- Azure CLI configurado
- Credenciais de Service Principal do Azure

## Gerenciamento do Ambiente

### Desativar Ambiente Virtual
```bash
deactivate
```

### Reativar Ambiente Virtual (sessões futuras)
```bash
# No Windows:
dino_env\Scripts\activate

# No Linux/Mac:
source dino_env/bin/activate
```
