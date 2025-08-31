# 🦕 DINO ARC - Data Infrastructure and Operations Automation & Resource Configuration

**Ferramenta CLI completa para automação de infraestrutura Azure com Databricks Premium, Unity Catalog e Serverless Compute.**

## 📋 **Índice**

- [🎯 Visão Geral](#-visão-geral)
- [⚡ Quick Start](#-quick-start)
- [🔧 Configuração do Ambiente](#-configuração-do-ambiente)
- [📦 Instalação de Dependências](#-instalação-de-dependências)
- [🚀 Uso da Ferramenta](#-uso-da-ferramenta)
- [🔐 Configuração do Serverless](#-configuração-do-serverless)
- [📊 Componentes Criados](#-componentes-criados)
- [🔍 Troubleshooting](#-troubleshooting)
- [📖 Documentação Detalhada](#-documentação-detalhada)

---

## 🎯 **Visão Geral**

O **DINO ARC** é uma ferramenta CLI que automatiza completamente a criação e configuração de infraestrutura Azure para projetos de dados, incluindo:

- ✅ **Azure Resource Group** com configurações optimizadas
- ✅ **Azure Key Vault** para gestão segura de secrets
- ✅ **Service Principal** com permissões adequadas
- ✅ **Azure SQL Database** com configurações de performance
- ✅ **Databricks Premium** com Unity Catalog
- ✅ **Serverless Compute** para workflows, notebooks e pipelines
- ✅ **SQL Warehouse Serverless** para analytics
- ✅ **Arquitetura Medallion** (Bronze, Silver, Gold, Workspace)

### 🌟 **Características Principais**

- 🔄 **Terraform**: Infraestrutura como código
- 🔐 **Service Principal**: Autenticação segura
- 📊 **Unity Catalog**: Governança de dados
- ⚡ **Serverless**: Compute otimizado e econômico
- 🎯 **East US 2**: Região otimizada
- 🔒 **Sem Soft Delete**: Recursos limpos
- 📋 **Logging Detalhado**: Diagnósticos completos

---

## ⚡ **Quick Start**

### Comando Rápido de Apply
```cmd
cd "c:\caminho\para\dino_2\dino_arc" && python -m src.cli --client-id SEU_CLIENT_ID --client-secret SEU_CLIENT_SECRET --tenant_id SEU_TENANT_ID --subscription-id SEU_SUBSCRIPTION_ID --action apply --projeto data-master --location "East US 2"
```

### Comando Rápido de Destroy
```cmd
cd "c:\caminho\para\dino_2\dino_arc" && python -m src.cli --client-id SEU_CLIENT_ID --client-secret SEU_CLIENT_SECRET --tenant_id SEU_TENANT_ID --subscription-id SEU_SUBSCRIPTION_ID --action destroy --projeto data-master --location "East US 2"
```

---

## 🔧 **Configuração do Ambiente**

### **1. Pré-requisitos**

#### 🐍 **Python 3.8+**
```cmd
python --version
# Deve retornar Python 3.8 ou superior
```

#### 🔧 **Terraform 1.0+**
```cmd
# Download do Terraform
# https://www.terraform.io/downloads.html
terraform --version
# Deve retornar Terraform v1.0 ou superior
```

#### ☁️ **Azure CLI**
```cmd
# Download do Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
az --version
# Deve retornar versão do Azure CLI
```

### **2. Clonagem do Repositório**
```cmd
git clone https://github.com/ramosbrunno/dino_2.git
cd dino_2/dino_arc
```

### **3. Configuração do Service Principal**

#### 🔐 **Criar Service Principal**
```cmd
az login
az ad sp create-for-rbac --name "data-master-spn" --role="Contributor" --scopes="/subscriptions/SEU_SUBSCRIPTION_ID"
```

#### 📋 **Obter Informações**
Anote as seguintes informações retornadas:
- `appId` = **client_id**
- `password` = **client_secret**
- `tenant` = **tenant_id**
- `subscription_id` = **subscription_id**

#### ⚙️ **Permissões Adicionais**
```cmd
# Permissão para Key Vault
az role assignment create --assignee SEU_CLIENT_ID --role "Key Vault Administrator" --scope "/subscriptions/SEU_SUBSCRIPTION_ID"

# Permissão para SQL Server
az role assignment create --assignee SEU_CLIENT_ID --role "SQL Server Contributor" --scope "/subscriptions/SEU_SUBSCRIPTION_ID"
```

---

## 📦 **Instalação de Dependências**

### **1. Ambiente Virtual (Recomendado)**
```cmd
# Criar ambiente virtual
python -m venv dino_env

# Ativar ambiente virtual
# Windows:
dino_env\Scripts\activate
# Linux/Mac:
source dino_env/bin/activate
```

### **2. Instalar Dependências Python**
```cmd
# Instalar dependências básicas
pip install -r requirements.txt

# Instalar Databricks SDK (obrigatório para Serverless)
pip install databricks-sdk

# Instalar dependências de desenvolvimento (opcional)
pip install -e .
```

### **3. Verificar Instalação**
```cmd
# Verificar se todas as dependências foram instaladas
python -c "import databricks.sdk; print('✅ Databricks SDK instalado')"
python -c "import azure.identity; print('✅ Azure Identity instalado')"
python -c "import terraform; print('✅ Terraform disponível')" 2>/dev/null || echo "⚠️ Terraform CLI necessário"
```

---

## 🚀 **Uso da Ferramenta**

### **1. Sintaxe Básica**
```cmd
python -m src.cli [OPÇÕES]
```

### **2. Parâmetros Obrigatórios**
- `--client-id`: Service Principal Client ID
- `--client-secret`: Service Principal Client Secret  
- `--tenant_id`: Azure Tenant ID
- `--subscription-id`: Azure Subscription ID
- `--action`: Ação a executar (`apply` ou `destroy`)
- `--projeto`: Nome do projeto
- `--location`: Região Azure (`"East US 2"`)

### **3. Exemplo Completo - Apply**
```cmd
cd "c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_arc"

python -m src.cli \
  --client-id Service Principal Client ID \
  --client-secret Service Principal Client Secret \
  --tenant_id Azure Tenant ID \
  --subscription-id Azure Subscription ID \
  --action apply \
  --projeto data-master \
  --location "East US 2"
```

### **4. Exemplo Completo - Destroy**
```cmd
python -m src.cli \
  --client-id Service Principal Client ID \
  --client-secret Service Principal Client Secret \
  --tenant_id Azure Tenant ID \
  --subscription-id Azure Subscription ID \
  --action destroy \
  --projeto data-master \
  --location "East US 2"
```

---

## 🔐 **Configuração do Serverless**

### **🎯 Habilitação Automática vs Manual**

O DINO ARC tentará habilitar automaticamente o **"Serverless compute for workflows, notebooks, and Lakeflow Declarative Pipelines"**, mas se a habilitação automática falhar, siga os passos manuais abaixo.

### **📋 Passo a Passo Manual (Baseado na Documentação Microsoft)**

#### **1. Acesso ao Databricks Account Console**
```
🌐 URL: https://accounts.azuredatabricks.net
🔐 Login: Use as credenciais do Service Principal ou conta administrativa
```

#### **2. Navegação para Feature Enablement**
```
⚙️ Settings → Feature enablement
```

#### **3. Habilitar Serverless Compute**
Marque as seguintes opções:
- ✅ **Serverless compute for workflows, notebooks, and Lakeflow Declarative Pipelines**
- ✅ **Unity Catalog** (se ainda não habilitado)
- ✅ **Enhanced security monitoring** (opcional mas recomendado)

#### **4. Configurações Account-Level**
```
📝 Navegue para: Settings → Account settings → Workspace settings
✅ Habilite: "Allow serverless compute"
✅ Habilite: "Enable serverless SQL warehouses"
```

#### **5. Configurações de Rede (se necessário)**
```
🌐 Navegue para: Settings → Network → Serverless
✅ Configure: "Enable serverless compute networking"
⚠️ Nota: O DINO ARC não configura redes customizadas - usa defaults seguros
```

#### **6. Tempo de Propagação**
```
⏳ Aguarde: 5-10 minutos para propagação das configurações
🔄 Verifique: Execute novamente o comando apply para validar
```

### **🔍 Verificação de Status**

#### **Via CLI do DINO ARC**
```cmd
# O comando apply mostrará o status do serverless
python -m src.cli ... --action apply
```

#### **Via Databricks Workspace**
```
🌐 Acesse: Seu workspace Databricks
⚙️ Settings → Admin Console → Workspace settings
🔍 Verifique: "Serverless compute" deve estar "Enabled"
```

### **📊 Logs Detalhados**

O DINO ARC cria logs detalhados em:
```
📁 logs/serverless_enablement_[timestamp].log
```

Este arquivo contém:
- 🔍 **Stacktraces completos** de erros
- 📝 **APIs tentadas** e suas respostas  
- 🔐 **Fluxo de autenticação** detalhado
- ⚙️ **Configurações aplicadas** e falhadas

### **🚨 Troubleshooting Serverless**

#### **Problema: "Databricks SDK não disponível"**
```cmd
# Solução: Instalar o SDK
pip install databricks-sdk
```

#### **Problema: "Account-level APIs requerem account_id"**
```
✅ Solução: Configuração manual via Account Console (passos acima)
```

#### **Problema: "WorkspaceConfAPI.set_status() argumentos incorretos"**
```
✅ Solução: O DINO ARC tenta múltiplas assinaturas automaticamente
📋 Verifique: logs/ para detalhes técnicos
```

#### **Problema: "Serverless não habilitado após configuração"**
```
⏳ Aguarde: 5-10 minutos para propagação
🔄 Execute: comando apply novamente
📞 Contate: Suporte Databricks se persistir
```

---

## 📊 **Componentes Criados**

### **🏗️ Infraestrutura Base**
- **Resource Group**: `{projeto}-{ambiente}-rsg`
- **Key Vault**: `{projeto}-{ambiente}-akv-[random]`
- **Service Principal**: `{projeto}-{ambiente}-spn`

### **🧮 Databricks Premium**
- **Workspace**: `{projeto}-{ambiente}-dbw-[random]`
- **Pricing Tier**: Premium (necessário para Unity Catalog)
- **Region**: East US 2
- **Network**: Default (otimizado para Serverless)

### **📊 Unity Catalog**
- **Metastore**: `{projeto}-{ambiente}-metastore`
- **Storage Account**: `{projeto}{ambiente}ucsa[random]`
- **Catalog**: `{projeto}_{ambiente}`

### **🗂️ Schemas (Arquitetura Medallion)**
- **Bronze**: `{projeto}_{ambiente}.bronze`
- **Silver**: `{projeto}_{ambiente}.silver`  
- **Gold**: `{projeto}_{ambiente}.gold`
- **Workspace**: `{projeto}_{ambiente}.workspace`

### **🏭 SQL Warehouse**
- **Nome**: `{projeto}-{ambiente}-warehouse`
- **Tipo**: Serverless
- **Size**: X-Small (escalável automaticamente)
- **Auto-stop**: 10 minutos

### **⚡ Serverless Compute**
- **Workflows**: Habilitado para Jobs
- **Notebooks**: Habilitado para desenvolvimento
- **Pipelines**: Habilitado para Lakeflow Declarative Pipelines
- **Policies**: Política customizada para Serverless

---

## 🔍 **Troubleshooting**

### **🚨 Problemas Comuns**

#### **1. Erro de Autenticação**
```
❌ Erro: "Authentication failed"
✅ Solução:
   1. Verificar client_id, client_secret, tenant_id
   2. Verificar permissões do Service Principal
   3. Executar: az login para testar credenciais
```

#### **2. Terraform Não Encontrado**
```
❌ Erro: "terraform not found"
✅ Solução:
   1. Instalar Terraform: https://www.terraform.io/downloads.html
   2. Adicionar ao PATH do sistema
   3. Verificar: terraform --version
```

#### **3. Dependências Python**
```
❌ Erro: "Module not found"
✅ Solução:
   1. Ativar ambiente virtual: dino_env\Scripts\activate
   2. Instalar dependências: pip install -r requirements.txt
   3. Instalar Databricks SDK: pip install databricks-sdk
```

#### **4. Permissões Insuficientes**
```
❌ Erro: "Insufficient privileges"
✅ Solução:
   1. Verificar papel do Service Principal: Contributor
   2. Adicionar permissões específicas (ver seção Configuração)
   3. Aguardar propagação das permissões (até 10 minutos)
```

#### **5. Recursos Já Existem**
```
❌ Erro: "Resource already exists"
✅ Solução:
   1. Executar destroy primeiro: --action destroy
   2. Aguardar conclusão completa
   3. Executar apply novamente: --action apply
```

### **📋 Logs e Diagnósticos**

#### **Localização dos Logs**
```
📁 logs/serverless_enablement_[timestamp].log - Logs de Serverless
📁 terraform/ - Estados do Terraform
📁 dino_env/ - Ambiente virtual Python
```

#### **Comandos de Diagnóstico**
```cmd
# Verificar versões
python --version
terraform --version
az --version

# Verificar dependências Python
pip list | findstr databricks
pip list | findstr azure

# Verificar autenticação Azure
az account show

# Verificar estado do Terraform
cd terraform && terraform show
```

---

## 📖 **Documentação Detalhada**

### **🔗 Links Úteis**

- **[Microsoft Databricks Serverless](https://docs.microsoft.com/en-us/azure/databricks/serverless-compute/)**
- **[Unity Catalog Documentation](https://docs.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/)**
- **[Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)**
- **[Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/reference-index)**

### **📁 Estrutura do Projeto**
```
dino_arc/
├── src/
│   ├── cli.py                      # CLI principal
│   ├── sdk/
│   │   └── azure_auth.py          # Autenticação Azure
│   ├── databricks_config/
│   │   ├── unity_catalog_setup.py # Configuração Unity Catalog
│   │   └── enable_serverless.py   # Habilitação Serverless
│   └── terraform/
│       └── terraform_manager.py   # Gerenciamento Terraform
├── terraform/
│   ├── foundation/                 # Infraestrutura base
│   ├── databricks/                # Databricks Premium
│   └── sql_database/              # Azure SQL Database
├── logs/                          # Logs detalhados
├── requirements.txt               # Dependências Python
├── setup.py                      # Configuração do pacote
└── README.md                     # Este arquivo
```

### **🎯 Casos de Uso**

#### **1. Desenvolvimento Local**
```cmd
# Criar ambiente de desenvolvimento
python -m src.cli --action apply --projeto dev-local --location "East US 2" [credenciais]
```

#### **2. Ambiente de Produção**
```cmd
# Criar ambiente de produção
python -m src.cli --action apply --projeto prod-data --location "East US 2" [credenciais]
```

#### **3. Limpeza Completa**
```cmd
# Remover todos os recursos
python -m src.cli --action destroy --projeto nome-projeto --location "East US 2" [credenciais]
```

---

## 📞 **Suporte e Contribuição**

### **🐛 Reportar Problemas**
1. Verificar logs em `logs/`
2. Executar comandos de diagnóstico
3. Abrir issue no repositório com:
   - Comando executado
   - Log de erro completo
   - Versões das ferramentas

### **🤝 Contribuir**
1. Fork do repositório
2. Criar branch feature
3. Commit das mudanças
4. Abrir Pull Request

### **📄 Licença**
Este projeto está sob licença MIT - veja o arquivo LICENSE para detalhes.

---

## 🎉 **Conclusão**

O **DINO ARC** fornece uma solução completa e automatizada para criação de infraestrutura Azure com Databricks Premium e Serverless Compute. Com este README, você tem todas as informações necessárias para:

✅ **Configurar** o ambiente corretamente  
✅ **Executar** os comandos com segurança  
✅ **Habilitar** Serverless Compute automaticamente ou manualmente  
✅ **Diagnosticar** e resolver problemas  
✅ **Manter** a infraestrutura de forma eficiente  

🚀 **Happy Data Engineering!** 🚀
